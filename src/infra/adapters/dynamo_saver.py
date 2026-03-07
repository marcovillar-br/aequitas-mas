"""
DynamoDB checkpointer adapter for LangGraph.

This module implements a custom checkpointer using AWS DynamoDB
to provide Serverless persistence for the Aequitas-MAS graph,
adhering strictly to the Dependency Inversion Principle.
"""

import os
import structlog
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import Binary
from botocore.exceptions import ClientError
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langchain_core.runnables import RunnableConfig

logger = structlog.get_logger(__name__)


class DynamoDBSaver(BaseCheckpointSaver):
    """
    Serverless persistence adapter using AWS DynamoDB.
    
    Inherits from langgraph's BaseCheckpointSaver to maintain
    graph isolation from the persistence layer.
    """

    def __init__(self, table_name: str) -> None:
        """
        Initialize the DynamoDB saver.
        
        Enforces Zero Trust security by strictly relying on environment
        variables for AWS credentials and region configuration.
        
        Args:
            table_name (str): The name of the DynamoDB table to use.
        """
        super().__init__()
        self.table_name = table_name
        
        # Zero Trust enforcement: Fetch region strictly from environment.
        aws_region: Optional[str] = os.getenv("AWS_REGION")
        if not aws_region:
            raise ValueError("AWS_REGION environment variable is not set. Zero Trust policy violation.")
            
        self.dynamodb = boto3.resource("dynamodb", region_name=aws_region)
        self.table = self.dynamodb.Table(self.table_name)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Fetch a checkpoint tuple from DynamoDB.
        
        Args:
            config (RunnableConfig): The configuration identifying the checkpoint.
            
        Returns:
            Optional[CheckpointTuple]: The checkpoint tuple if found, None otherwise.
        """
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id")
        checkpoint_id = configurable.get("checkpoint_id")

        if not thread_id:
            logger.warning("get_tuple_called_without_thread_id", config=config)
            return None

        try:
            if checkpoint_id:
                # Retrieve specific checkpoint
                response = self.table.get_item(
                    Key={
                        "thread_id": thread_id,
                        "checkpoint_id": checkpoint_id,
                    }
                )
                item = response.get("Item")
            else:
                # Query for the latest checkpoint for the thread
                response = self.table.query(
                    KeyConditionExpression=Key("thread_id").eq(thread_id),
                    ScanIndexForward=False,  # Sort descending
                    Limit=1,
                )
                items = response.get("Items", [])
                item = items[0] if items else None

            if not item:
                return None

            checkpoint = self.serde.loads(item["checkpoint"].value)
            metadata = self.serde.loads(item["metadata"].value)

            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": item["checkpoint_id"],
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                pending_writes=None,
            )

        except ClientError as e:
            logger.error(
                "dynamodb_get_tuple_failed",
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                error=str(e),
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                "dynamodb_get_tuple_unexpected_error",
                thread_id=thread_id,
                error=str(e),
                exc_info=True,
            )
            return None

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, str | float | int],
    ) -> RunnableConfig:
        """
        Save a checkpoint to DynamoDB.
        
        Args:
            config (RunnableConfig): The configuration identifying the checkpoint.
            checkpoint (Checkpoint): The checkpoint data to save.
            metadata (CheckpointMetadata): The metadata associated with the checkpoint.
            new_versions (dict[str, str | float | int]): The new channel versions.
            
        Returns:
            RunnableConfig: The updated configuration.
        """
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id")
        checkpoint_id = checkpoint["id"]

        if not thread_id:
            logger.error("put_called_without_thread_id", config=config)
            raise ValueError("thread_id is required in config['configurable'] to save a checkpoint.")

        # Serialize using LangGraph's internal serde and store as Binary to avoid DynamoDB type issues
        checkpoint_blob = self.serde.dumps(checkpoint)
        metadata_blob = self.serde.dumps(metadata)

        item = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint": Binary(checkpoint_blob),
            "metadata": Binary(metadata_blob),
        }

        try:
            self.table.put_item(Item=item)
            logger.debug(
                "checkpoint_saved_to_dynamodb",
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
            )
        except ClientError as e:
            logger.error(
                "dynamodb_put_item_failed",
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                error=str(e),
                exc_info=True,
            )
        except Exception as e:
            logger.error(
                "dynamodb_put_unexpected_error",
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                error=str(e),
                exc_info=True,
            )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

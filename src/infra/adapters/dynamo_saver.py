"""DynamoDB adapter scaffold for LangGraph checkpoint persistence."""

import os
from datetime import datetime, timezone
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import Binary
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)


class DynamoDBSaver(BaseCheckpointSaver):
    """Checkpoint saver with dependency injection for DynamoDB table access."""

    def __init__(self, table=None):
        """Initialize with an injected table, or create one from runtime config."""
        super().__init__()
        if table is None:
            self.table = boto3.resource("dynamodb").Table(
                os.getenv("DYNAMODB_TABLE_NAME", "aequitas_state")
            )
        else:
            self.table = table

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Return a stored checkpoint tuple for the provided runnable configuration."""
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id")
        checkpoint_id = configurable.get("checkpoint_id")

        if not thread_id:
            return None

        if checkpoint_id:
            response = self.table.get_item(
                Key={"thread_id": thread_id, "checkpoint_id": checkpoint_id}
            )
            item = response.get("Item")
        else:
            response = self.table.query(
                KeyConditionExpression=Key("thread_id").eq(thread_id),
                ScanIndexForward=False,
                Limit=1,
            )
            items = response.get("Items", [])
            item = items[0] if items else None

        if item is None:
            return None

        checkpoint_binary = item["checkpoint"]
        metadata_binary = item["metadata"]

        checkpoint_bytes = (
            checkpoint_binary.value
            if isinstance(checkpoint_binary, Binary)
            else checkpoint_binary
        )
        metadata_bytes = (
            metadata_binary.value if isinstance(metadata_binary, Binary) else metadata_binary
        )

        loaded_checkpoint = self.serde.loads(checkpoint_bytes)
        loaded_metadata = self.serde.loads(metadata_bytes)

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": item["thread_id"],
                    "checkpoint_id": item["checkpoint_id"],
                }
            },
            checkpoint=loaded_checkpoint,
            metadata=loaded_metadata,
            pending_writes=None,
        )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Persist a checkpoint and return the resulting runnable configuration."""
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id")
        checkpoint_id = configurable.get("checkpoint_id")

        if not thread_id or not checkpoint_id:
            raise ValueError(
                "config['configurable'] must include both 'thread_id' and 'checkpoint_id'."
            )

        checkpoint_bytes = self.serde.dumps(checkpoint)
        metadata_bytes = self.serde.dumps(metadata)

        self.table.put_item(
            Item={
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "checkpoint": Binary(checkpoint_bytes),
                "metadata": Binary(metadata_bytes),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

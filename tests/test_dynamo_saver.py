"""
Unit tests for the DynamoDBSaver checkpointer adapter.
"""

import pytest
from botocore.exceptions import ClientError
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata

from src.infra.adapters.dynamo_saver import DynamoDBSaver
from boto3.dynamodb.types import Binary

# Dummy constants for testing
DUMMY_TABLE_NAME = "aequitas-checkpoints-test"
DUMMY_REGION = "us-east-1"
DUMMY_THREAD_ID = "thread-123"
DUMMY_CHECKPOINT_ID = "chkpt-456"

@pytest.fixture
def mock_aws_env(monkeypatch):
    """Fixture to mock AWS environment variables."""
    monkeypatch.setenv("AWS_REGION", DUMMY_REGION)

@pytest.fixture
def mock_boto3_resource(mocker):
    """Fixture to mock boto3.resource and return a mock table."""
    mock_resource = mocker.patch("boto3.resource")
    mock_table = mocker.MagicMock()
    mock_resource.return_value.Table.return_value = mock_table
    return mock_resource, mock_table

@pytest.fixture
def base_config() -> RunnableConfig:
    return {"configurable": {"thread_id": DUMMY_THREAD_ID}}

@pytest.fixture
def dummy_checkpoint() -> Checkpoint:
    return {
        "v": 1,
        "id": DUMMY_CHECKPOINT_ID,
        "ts": "2024-01-01T00:00:00Z",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }

@pytest.fixture
def dummy_metadata() -> CheckpointMetadata:
    return {"source": "test", "step": 1}

def test_init_success(mock_aws_env, mock_boto3_resource):
    """Test successful initialization when AWS_REGION is set."""
    mock_resource, mock_table = mock_boto3_resource
    
    saver = DynamoDBSaver(table_name=DUMMY_TABLE_NAME)
    
    assert saver.table_name == DUMMY_TABLE_NAME
    mock_resource.assert_called_once_with("dynamodb", region_name=DUMMY_REGION)
    mock_resource.return_value.Table.assert_called_once_with(DUMMY_TABLE_NAME)

def test_init_missing_region(monkeypatch):
    """Test Zero Trust enforcement: raises ValueError if AWS_REGION is missing."""
    monkeypatch.delenv("AWS_REGION", raising=False)
    
    with pytest.raises(ValueError, match="AWS_REGION environment variable is not set"):
        DynamoDBSaver(table_name=DUMMY_TABLE_NAME)

def test_put_success(mock_aws_env, mock_boto3_resource, base_config, dummy_checkpoint, dummy_metadata):
    """Test successful put_item operation."""
    _, mock_table = mock_boto3_resource
    saver = DynamoDBSaver(table_name=DUMMY_TABLE_NAME)
    
    result = saver.put(base_config, dummy_checkpoint, dummy_metadata, {})
    
    # Verify the returned config
    assert result == {
        "configurable": {
            "thread_id": DUMMY_THREAD_ID,
            "checkpoint_id": DUMMY_CHECKPOINT_ID,
        }
    }
    
    # Verify DynamoDB put_item was called
    mock_table.put_item.assert_called_once()
    call_kwargs = mock_table.put_item.call_args[1]
    assert "Item" in call_kwargs
    item = call_kwargs["Item"]
    assert item["thread_id"] == DUMMY_THREAD_ID
    assert item["checkpoint_id"] == DUMMY_CHECKPOINT_ID
    assert isinstance(item["checkpoint"], Binary)
    assert isinstance(item["metadata"], Binary)

def test_get_tuple_latest(mock_aws_env, mock_boto3_resource, base_config, dummy_checkpoint, dummy_metadata):
    """Test successful query for the latest checkpoint."""
    _, mock_table = mock_boto3_resource
    saver = DynamoDBSaver(table_name=DUMMY_TABLE_NAME)
    
    # Mock the query response
    checkpoint_blob = saver.serde.dumps(dummy_checkpoint)
    metadata_blob = saver.serde.dumps(dummy_metadata)
    
    class MockBinary:
        def __init__(self, val):
            self.value = val

    mock_table.query.return_value = {
        "Items": [
            {
                "thread_id": DUMMY_THREAD_ID,
                "checkpoint_id": DUMMY_CHECKPOINT_ID,
                "checkpoint": MockBinary(checkpoint_blob),
                "metadata": MockBinary(metadata_blob),
            }
        ]
    }
    
    result = saver.get_tuple(base_config)
    
    assert result is not None
    assert result.config["configurable"]["thread_id"] == DUMMY_THREAD_ID
    assert result.config["configurable"]["checkpoint_id"] == DUMMY_CHECKPOINT_ID
    assert result.checkpoint == dummy_checkpoint
    assert result.metadata == dummy_metadata
    
    mock_table.query.assert_called_once()
    # Verify it queried by thread_id and sorted descending
    call_kwargs = mock_table.query.call_args[1]
    assert call_kwargs["ScanIndexForward"] is False
    assert call_kwargs["Limit"] == 1

def test_botocore_client_error_handling(mock_aws_env, mock_boto3_resource, base_config, dummy_checkpoint, dummy_metadata, mocker):
    """Test graceful handling and logging of boto3 ClientError."""
    _, mock_table = mock_boto3_resource
    saver = DynamoDBSaver(table_name=DUMMY_TABLE_NAME)
    
    # Mock logger to verify error was logged
    mock_logger = mocker.patch("src.infra.adapters.dynamo_saver.logger")
    
    # Create a dummy ClientError
    error_response = {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Rate exceeded'}}
    client_error = ClientError(error_response, 'PutItem')
    
    # Set the mock to raise the ClientError on put_item
    mock_table.put_item.side_effect = client_error
    
    # Execute put (should not raise)
    saver.put(base_config, dummy_checkpoint, dummy_metadata, {})
    
    # Verify the error was logged
    mock_logger.error.assert_called_with(
        "dynamodb_put_item_failed",
        thread_id=DUMMY_THREAD_ID,
        checkpoint_id=DUMMY_CHECKPOINT_ID,
        error=str(client_error),
        exc_info=True,
    )

    # Set the mock to raise the ClientError on query
    mock_table.query.side_effect = client_error
    
    # Execute get_tuple (should return None and not raise)
    result = saver.get_tuple(base_config)
    
    assert result is None
    # Verify the error was logged for get_tuple (checkpoint_id is None since it wasn't in config)
    mock_logger.error.assert_called_with(
        "dynamodb_get_tuple_failed",
        thread_id=DUMMY_THREAD_ID,
        checkpoint_id=None,
        error=str(client_error),
        exc_info=True,
    )

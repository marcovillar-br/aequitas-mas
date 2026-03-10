"""Unit tests for the DynamoDBSaver adapter using dependency-injected mocks."""

from unittest.mock import MagicMock

import pytest

# Skip the entire module gracefully when boto3 is not installed
# (e.g. CI environments using `poetry install --without infra`).
pytest.importorskip("boto3")

from boto3.dynamodb.conditions import Key  # noqa: E402
from boto3.dynamodb.types import Binary  # noqa: E402

from src.infra.adapters.dynamo_saver import DynamoDBSaver  # noqa: E402


@pytest.fixture
def mock_table() -> MagicMock:
    """Provide a mocked DynamoDB table for zero-network unit tests."""
    return MagicMock()


@pytest.fixture
def saver(mock_table: MagicMock) -> DynamoDBSaver:
    """Create a saver instance with an injected mocked table."""
    return DynamoDBSaver(table=mock_table)


@pytest.fixture
def dummy_checkpoint() -> dict:
    """Build a valid checkpoint payload for serializer round-trips."""
    return {
        "v": 1,
        "id": "checkpoint-001",
        "ts": "2026-03-08T00:00:00Z",
        "channel_values": {"fisher_score": None, "signal": 0.91},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }


@pytest.fixture
def dummy_metadata() -> dict:
    """Build metadata payload used in persistence calls."""
    return {"source": "unit-test", "step": 3}


def test_put_checkpoint(
    saver: DynamoDBSaver,
    mock_table: MagicMock,
    dummy_checkpoint: dict,
    dummy_metadata: dict,
) -> None:
    """Store a checkpoint and verify serialized payload is persisted."""
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_id": "checkpoint-001"}}

    result = saver.put(config, dummy_checkpoint, dummy_metadata, {})

    mock_table.put_item.assert_called_once()
    put_kwargs = mock_table.put_item.call_args.kwargs
    assert "Item" in put_kwargs

    item = put_kwargs["Item"]
    assert item["thread_id"] == "thread-1"
    assert item["checkpoint_id"] == "checkpoint-001"
    assert isinstance(item["checkpoint"], Binary)
    assert isinstance(item["metadata"], Binary)
    assert item["timestamp"]

    serialized_checkpoint = saver.serde.loads(item["checkpoint"].value)
    serialized_metadata = saver.serde.loads(item["metadata"].value)
    assert serialized_checkpoint["channel_values"]["fisher_score"] is None
    assert serialized_metadata == dummy_metadata

    assert result == {
        "configurable": {"thread_id": "thread-1", "checkpoint_id": "checkpoint-001"}
    }


def test_get_tuple_with_checkpoint_id(
    saver: DynamoDBSaver,
    mock_table: MagicMock,
    dummy_checkpoint: dict,
    dummy_metadata: dict,
) -> None:
    """Read a checkpoint by explicit checkpoint_id using get_item."""
    checkpoint_bytes = saver.serde.dumps(dummy_checkpoint)
    metadata_bytes = saver.serde.dumps(dummy_metadata)
    mock_table.get_item.return_value = {
        "Item": {
            "thread_id": "thread-1",
            "checkpoint_id": "checkpoint-001",
            "checkpoint": Binary(checkpoint_bytes),
            "metadata": Binary(metadata_bytes),
        }
    }

    config = {"configurable": {"thread_id": "thread-1", "checkpoint_id": "checkpoint-001"}}
    result = saver.get_tuple(config)

    mock_table.get_item.assert_called_once_with(
        Key={"thread_id": "thread-1", "checkpoint_id": "checkpoint-001"}
    )
    assert result is not None
    assert result.config["configurable"]["thread_id"] == "thread-1"
    assert result.config["configurable"]["checkpoint_id"] == "checkpoint-001"
    assert result.checkpoint == dummy_checkpoint
    assert result.metadata == dummy_metadata


def test_get_tuple_latest(
    saver: DynamoDBSaver,
    mock_table: MagicMock,
    dummy_checkpoint: dict,
    dummy_metadata: dict,
) -> None:
    """Read the latest checkpoint when checkpoint_id is not provided."""
    checkpoint_bytes = saver.serde.dumps(dummy_checkpoint)
    metadata_bytes = saver.serde.dumps(dummy_metadata)
    mock_table.query.return_value = {
        "Items": [
            {
                "thread_id": "thread-1",
                "checkpoint_id": "checkpoint-001",
                "checkpoint": Binary(checkpoint_bytes),
                "metadata": Binary(metadata_bytes),
            }
        ]
    }

    config = {"configurable": {"thread_id": "thread-1"}}
    result = saver.get_tuple(config)

    mock_table.query.assert_called_once()
    query_kwargs = mock_table.query.call_args.kwargs
    assert query_kwargs["KeyConditionExpression"] == Key("thread_id").eq("thread-1")
    assert query_kwargs["ScanIndexForward"] is False
    assert query_kwargs["Limit"] == 1

    assert result is not None
    assert result.config["configurable"]["thread_id"] == "thread-1"
    assert result.config["configurable"]["checkpoint_id"] == "checkpoint-001"
    assert result.checkpoint == dummy_checkpoint
    assert result.metadata == dummy_metadata


def test_get_tuple_not_found(saver: DynamoDBSaver, mock_table: MagicMock) -> None:
    """Return None when no checkpoint is stored for the given identifiers."""
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_id": "missing-checkpoint"}}
    mock_table.get_item.return_value = {}

    result = saver.get_tuple(config)

    mock_table.get_item.assert_called_once_with(
        Key={"thread_id": "thread-1", "checkpoint_id": "missing-checkpoint"}
    )
    assert result is None

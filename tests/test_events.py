from unittest.mock import MagicMock, patch

from src.services.events import (
    get_event,
    save_event,
    update_event_status,
)


@patch.dict("os.environ", {"EVENTS_TABLE": "relay-events"})
@patch("src.services.events.boto3.resource")
def test_save_event(mock_boto_resource):
    mock_dynamodb = MagicMock()
    mock_table = MagicMock()

    mock_boto_resource.return_value = mock_dynamodb
    mock_dynamodb.Table.return_value = mock_table

    notification = {
        "event_id": "event-123",
        "recipient": "test@example.com",
        "status": "queued",
    }

    save_event(notification)

    mock_boto_resource.assert_called_once_with("dynamodb")
    mock_dynamodb.Table.assert_called_once_with("relay-events")

    mock_table.put_item.assert_called_once_with(
        Item=notification
    )


@patch.dict("os.environ", {"EVENTS_TABLE": "relay-events"})
@patch("src.services.events.boto3.resource")
def test_get_existing_event(mock_boto_resource):
    mock_dynamodb = MagicMock()
    mock_table = MagicMock()

    mock_boto_resource.return_value = mock_dynamodb
    mock_dynamodb.Table.return_value = mock_table

    stored_event = {
        "event_id": "event-123",
        "status": "delivered",
    }

    mock_table.get_item.return_value = {
        "Item": stored_event
    }

    result = get_event("event-123")

    assert result == stored_event

    mock_table.get_item.assert_called_once_with(
        Key={"event_id": "event-123"}
    )


@patch.dict("os.environ", {"EVENTS_TABLE": "relay-events"})
@patch("src.services.events.boto3.resource")
def test_get_missing_event(mock_boto_resource):
    mock_dynamodb = MagicMock()
    mock_table = MagicMock()

    mock_boto_resource.return_value = mock_dynamodb
    mock_dynamodb.Table.return_value = mock_table

    mock_table.get_item.return_value = {}

    result = get_event("missing-event")

    assert result is None


@patch.dict("os.environ", {"EVENTS_TABLE": "relay-events"})
@patch("src.services.events.boto3.resource")
def test_update_event_status_without_attributes(
    mock_boto_resource,
):
    mock_dynamodb = MagicMock()
    mock_table = MagicMock()

    mock_boto_resource.return_value = mock_dynamodb
    mock_dynamodb.Table.return_value = mock_table

    update_event_status(
        "event-123",
        "processing",
    )

    mock_table.update_item.assert_called_once_with(
        Key={"event_id": "event-123"},
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={
            "#status": "status",
        },
        ExpressionAttributeValues={
            ":status": "processing",
        },
    )


@patch.dict("os.environ", {"EVENTS_TABLE": "relay-events"})
@patch("src.services.events.boto3.resource")
def test_update_event_status_with_attributes(
    mock_boto_resource,
):
    mock_dynamodb = MagicMock()
    mock_table = MagicMock()

    mock_boto_resource.return_value = mock_dynamodb
    mock_dynamodb.Table.return_value = mock_table

    update_event_status(
        "event-123",
        "delivered",
        delivered_at="2026-08-21T13:00:00+00:00",
        email_message_id="ses-message-123",
    )

    mock_table.update_item.assert_called_once_with(
        Key={"event_id": "event-123"},
        UpdateExpression=(
            "SET #status = :status, "
            "#attr0 = :attr0, "
            "#attr1 = :attr1"
        ),
        ExpressionAttributeNames={
            "#status": "status",
            "#attr0": "delivered_at",
            "#attr1": "email_message_id",
        },
        ExpressionAttributeValues={
            ":status": "delivered",
            ":attr0": "2026-08-21T13:00:00+00:00",
            ":attr1": "ses-message-123",
        },
    )
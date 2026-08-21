import json
from unittest.mock import MagicMock, patch

from src.services.queue import queue_notification


@patch.dict(
    "os.environ",
    {"QUEUE_URL": "https://sqs.example.com/test-queue"},
)
@patch("src.services.queue.boto3.client")
def test_queue_notification(mock_boto_client):
    mock_sqs = MagicMock()
    mock_boto_client.return_value = mock_sqs

    mock_sqs.send_message.return_value = {
        "MessageId": "queue-message-123"
    }

    notification = {
        "event_id": "event-123",
        "recipient": "test@example.com",
        "subject": "Hello",
        "message": "Relay works",
        "status": "queued",
    }

    result = queue_notification(notification)

    assert result == "queue-message-123"

    mock_boto_client.assert_called_once_with("sqs")

    mock_sqs.send_message.assert_called_once_with(
        QueueUrl="https://sqs.example.com/test-queue",
        MessageBody=json.dumps(notification),
    )
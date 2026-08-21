import json
from unittest.mock import patch

from src.worker.deliver_notification import lambda_handler


@patch("src.worker.deliver_notification.update_event_status")
@patch("src.worker.deliver_notification.send_email")
def test_delivery_success(mock_send_email, mock_update_status):
    mock_send_email.return_value = "ses-message-123"

    event = {
        "Records": [
            {
                "body": json.dumps({
                    "event_id": "event-123",
                    "recipient": "test@example.com",
                    "subject": "Hello",
                    "message": "Relay works",
                })
            }
        ]
    }

    response = lambda_handler(event, None)

    assert response["processed"] == 1

    mock_send_email.assert_called_once_with(
        recipient="test@example.com",
        subject="Hello",
        message="Relay works",
    )

    mock_update_status.assert_called_once()

    args, kwargs = mock_update_status.call_args

    assert args[0] == "event-123"
    assert args[1] == "delivered"
    assert "delivered_at" in kwargs
    assert kwargs["email_message_id"] == "ses-message-123"


@patch("src.worker.deliver_notification.update_event_status")
@patch("src.worker.deliver_notification.send_email")
def test_delivery_failure(mock_send_email, mock_update_status):
    mock_send_email.side_effect = Exception("SES unavailable")

    event = {
        "Records": [
            {
                "body": json.dumps({
                    "event_id": "event-123",
                    "recipient": "test@example.com",
                    "subject": "Hello",
                    "message": "Relay works",
                })
            }
        ]
    }

    try:
        lambda_handler(event, None)
        assert False, "Expected delivery to raise an exception"

    except Exception as error:
        assert str(error) == "SES unavailable"

    assert mock_update_status.call_count == 1

    args, kwargs = mock_update_status.call_args

    assert args[0] == "event-123"
    assert args[1] == "failed"
    assert "failed_at" in kwargs


@patch("src.worker.deliver_notification.update_event_status")
@patch("src.worker.deliver_notification.send_email")
def test_empty_queue_event(mock_send_email, mock_update_status):
    response = lambda_handler({"Records": []}, None)

    assert response["processed"] == 0

    mock_send_email.assert_not_called()
    mock_update_status.assert_not_called()
import json
from unittest.mock import patch

from src.api.create_event import lambda_handler


@patch("src.api.create_event.save_event")
@patch("src.api.create_event.queue_notification")
def test_create_event(mock_queue, mock_save_event):
    mock_queue.return_value = "test-message-id"

    event = {
        "body": json.dumps({
            "recipient": "test@example.com",
            "subject": "Hello",
            "message": "Relay works",
        })
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 202

    body = json.loads(response["body"])

    assert body["status"] == "queued"
    assert body["queue_message_id"] == "test-message-id"
    assert "event_id" in body

    mock_save_event.assert_called_once()
    mock_queue.assert_called_once()


@patch("src.api.create_event.save_event")
@patch("src.api.create_event.queue_notification")
def test_missing_fields(mock_queue, mock_save_event):
    event = {
        "body": json.dumps({
            "recipient": "test@example.com",
        })
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    mock_queue.assert_not_called()
    mock_save_event.assert_not_called()


@patch("src.api.create_event.save_event")
@patch("src.api.create_event.queue_notification")
def test_invalid_json(mock_queue, mock_save_event):
    event = {
        "body": "{invalid json"
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    mock_queue.assert_not_called()
    mock_save_event.assert_not_called()
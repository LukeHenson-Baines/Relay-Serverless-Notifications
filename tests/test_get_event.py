import json
from unittest.mock import patch

from src.api.get_event import lambda_handler


@patch("src.api.get_event.get_event")
def test_get_existing_event(mock_get_event):
    mock_get_event.return_value = {
        "event_id": "abc-123",
        "recipient": "test@example.com",
        "subject": "Hello",
        "message": "Relay works",
        "status": "queued",
        "created_at": "2026-08-21T12:00:00+00:00",
    }

    event = {
        "pathParameters": {
            "event_id": "abc-123"
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["event_id"] == "abc-123"
    assert body["status"] == "queued"

    mock_get_event.assert_called_once_with("abc-123")


@patch("src.api.get_event.get_event")
def test_event_not_found(mock_get_event):
    mock_get_event.return_value = None

    event = {
        "pathParameters": {
            "event_id": "does-not-exist"
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 404

    body = json.loads(response["body"])

    assert body["error"] == "Event not found"


@patch("src.api.get_event.get_event")
def test_missing_event_id(mock_get_event):
    event = {
        "pathParameters": {}
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    mock_get_event.assert_not_called()
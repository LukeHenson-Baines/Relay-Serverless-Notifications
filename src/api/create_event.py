import json

from src.models.notification import Notification
from src.services.queue import queue_notification
from src.services.events import save_event


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")

        recipient = body.get("recipient")
        subject = body.get("subject")
        message = body.get("message")

        if not all([recipient, subject, message]):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": json.dumps({
                    "error": "recipient, subject and message are required"
                }),
            }

        notification = Notification.create(
            recipient=recipient,
            subject=subject,
            message=message,
        )

        queue_message_id = queue_notification(
            notification.to_dict()
        )

        notification_data = notification.to_dict()

        save_event(notification_data)

        return {
            "statusCode": 202,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "event_id": notification.event_id,
                "status": notification.status,
                "queue_message_id": queue_message_id,
            }),
        }

    except (json.JSONDecodeError, TypeError):
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "error": "Invalid JSON request body"
            }),
        }
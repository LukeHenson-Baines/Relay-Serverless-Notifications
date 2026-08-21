import json
from datetime import datetime, timezone

from src.services.email import send_email
from src.services.events import update_event_status


def lambda_handler(event, context):
    for record in event.get("Records", []):
        notification = json.loads(record["body"])

        event_id = notification["event_id"]

        try:
            email_message_id = send_email(
                recipient=notification["recipient"],
                subject=notification["subject"],
                message=notification["message"],
            )

            update_event_status(
                event_id,
                "delivered",
                delivered_at=datetime.now(timezone.utc).isoformat(),
                email_message_id=email_message_id,
            )

        except Exception:
            update_event_status(
                event_id,
                "failed",
                failed_at=datetime.now(timezone.utc).isoformat(),
            )

            raise

    return {
        "processed": len(event.get("Records", []))
    }
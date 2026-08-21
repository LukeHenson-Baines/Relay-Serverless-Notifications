import json

from src.services.events import get_event


def lambda_handler(event, context):
    event_id = event.get("pathParameters", {}).get("event_id")

    if not event_id:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "error": "event_id is required"
            }),
        }

    notification = get_event(event_id)

    if notification is None:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "error": "Event not found"
            }),
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(notification),
    }
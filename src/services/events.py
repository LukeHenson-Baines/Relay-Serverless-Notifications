import os

import boto3


def save_event(notification: dict) -> None:
    table_name = os.environ["EVENTS_TABLE"]

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    table.put_item(
        Item=notification
    )


def get_event(event_id: str) -> dict | None:
    table_name = os.environ["EVENTS_TABLE"]

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={"event_id": event_id}
    )

    return response.get("Item")
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

def update_event_status(
    event_id: str,
    status: str,
    **attributes,
) -> None:
    table_name = os.environ["EVENTS_TABLE"]

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    update_expression = "SET #status = :status"
    expression_names = {
        "#status": "status",
    }
    expression_values = {
        ":status": status,
    }

    for index, (key, value) in enumerate(attributes.items()):
        name_key = f"#attr{index}"
        value_key = f":attr{index}"

        update_expression += f", {name_key} = {value_key}"
        expression_names[name_key] = key
        expression_values[value_key] = value

    table.update_item(
        Key={"event_id": event_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
    )
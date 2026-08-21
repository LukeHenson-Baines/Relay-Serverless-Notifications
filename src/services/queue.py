import json
import os

import boto3


def queue_notification(notification: dict) -> str:
    queue_url = os.environ["QUEUE_URL"]

    sqs = boto3.client("sqs")

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(notification),
    )

    return response["MessageId"]
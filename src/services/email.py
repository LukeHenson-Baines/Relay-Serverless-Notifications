import os

import boto3


def send_email(recipient: str, subject: str, message: str) -> str:
    source_email = os.environ["SOURCE_EMAIL"]

    ses = boto3.client("ses")

    response = ses.send_email(
        Source=source_email,
        Destination={
            "ToAddresses": [recipient],
        },
        Message={
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8",
            },
            "Body": {
                "Text": {
                    "Data": message,
                    "Charset": "UTF-8",
                },
            },
        },
    )

    return response["MessageId"]
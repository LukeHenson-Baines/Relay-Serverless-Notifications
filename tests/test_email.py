from unittest.mock import MagicMock, patch

from src.services.email import send_email


@patch.dict("os.environ", {"SOURCE_EMAIL": "sender@example.com"})
@patch("src.services.email.boto3.client")
def test_send_email(mock_boto_client):
    mock_ses = MagicMock()
    mock_boto_client.return_value = mock_ses

    mock_ses.send_email.return_value = {
        "MessageId": "ses-message-123"
    }

    result = send_email(
        recipient="recipient@example.com",
        subject="Hello",
        message="Relay works",
    )

    assert result == "ses-message-123"

    mock_boto_client.assert_called_once_with("ses")

    mock_ses.send_email.assert_called_once_with(
        Source="sender@example.com",
        Destination={
            "ToAddresses": ["recipient@example.com"],
        },
        Message={
            "Subject": {
                "Data": "Hello",
                "Charset": "UTF-8",
            },
            "Body": {
                "Text": {
                    "Data": "Relay works",
                    "Charset": "UTF-8",
                },
            },
        },
    )
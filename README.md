# Relay

Relay is a serverless asynchronous email notification service built with Python and AWS.

Applications submit an email notification through a REST API and receive an immediate response confirming that the notification has been queued. Relay then processes the notification asynchronously, delivers the email through Amazon SES, and records its delivery status in DynamoDB.

The project demonstrates event-driven architecture, asynchronous processing, Infrastructure as Code, REST API design, cloud-native development and automated testing using AWS services.

## Features

- REST API for submitting email notifications
- Asynchronous message processing using Amazon SQS
- Email delivery through Amazon SES
- Persistent notification status tracking with DynamoDB
- Unique UUID-based event identifiers
- Delivery and failure status recording
- REST endpoint for retrieving notification status
- AWS Lambda serverless compute
- Infrastructure defined using AWS SAM
- Automated unit testing with pytest
- IAM permissions scoped to individual Lambda responsibilities

## Architecture

```text
                           Client Application
                                   |
                                   |
                            POST /events
                                   |
                                   v
                           Amazon API Gateway
                                   |
                                   v
                         Create Event Lambda
                            /            \
                           /              \
                          v                v
                     DynamoDB            SQS
                   status: queued         |
                                         |
                                         v
                                  Delivery Lambda
                                    /         \
                                   /           \
                                  v             v
                            Amazon SES       DynamoDB
                                |          status: delivered
                                |            or failed
                                v
                           Email Recipient


                     GET /events/{event_id}
                                |
                                v
                       Amazon API Gateway
                                |
                                v
                         Get Event Lambda
                                |
                                v
                            DynamoDB
                                |
                                v
                         Event Status
```

### Notification lifecycle

A successful notification moves through the following states:

```text
POST /events
     |
     v
   queued
     |
     v
    SQS
     |
     v
Delivery Lambda
     |
     v
 Amazon SES
     |
     v
 delivered
```

If delivery fails, the event is instead recorded as:

```text
queued -> failed
```

The delivery worker re-raises delivery exceptions so failed SQS processing can be recognised and retried by AWS rather than silently discarded.

## How It Works

### 1. Submit a notification

A client sends a request to:

```http
POST /events
```

with a JSON body:

```json
{
  "recipient": "user@example.com",
  "subject": "Your report is ready",
  "message": "Your report has finished processing."
}
```

The Create Event Lambda:

1. validates the request;
2. generates a unique event ID;
3. records the notification in DynamoDB;
4. places the notification onto Amazon SQS; and
5. immediately returns `202 Accepted`.

Example response:

```json
{
  "event_id": "32cf0a1c-ccfe-4942-bc37-6084935edf8b",
  "status": "queued",
  "queue_message_id": "dcf29a00-9822-46c5-83d5-6635229f4d37"
}
```

The use of `202 Accepted` reflects that the request has been accepted for asynchronous processing rather than guaranteeing that email delivery has already completed.

### 2. Process the notification

Amazon SQS triggers the Delivery Lambda when a queued notification becomes available.

The worker:

1. reads the notification from the queue;
2. sends the email using Amazon SES;
3. records the SES message ID;
4. records the delivery timestamp; and
5. changes the DynamoDB event status to `delivered`.

If email delivery fails, the event is marked as `failed` and the exception is propagated so the failed queue processing can be handled by AWS.

### 3. Retrieve notification status

Clients can query:

```http
GET /events/{event_id}
```

For example:

```http
GET /events/32cf0a1c-ccfe-4942-bc37-6084935edf8b
```

A successfully delivered notification returns a record similar to:

```json
{
  "event_id": "32cf0a1c-ccfe-4942-bc37-6084935edf8b",
  "recipient": "user@example.com",
  "subject": "Your report is ready",
  "message": "Your report has finished processing.",
  "status": "delivered",
  "created_at": "2026-08-21T13:08:44.153749+00:00",
  "delivered_at": "2026-08-21T13:08:47.200319+00:00",
  "email_message_id": "..."
}
```

If the event does not exist, Relay returns `404 Not Found`.

## Why Asynchronous Delivery?

Email delivery is deliberately separated from the API request.

A simpler implementation could call an email provider directly from the HTTP request:

```text
Client -> API -> Send Email -> Response
```

Relay instead uses:

```text
Client -> API -> Queue -> Response
                   |
                   v
             Delivery Worker
                   |
                   v
                 Email
```

This means the calling application does not have to wait for email delivery to complete.

Amazon SQS also decouples notification creation from notification delivery. Temporary problems with the downstream delivery process therefore do not require the original application to remain connected while Relay processes the notification.

## AWS Services

| Service | Purpose |
|---|---|
| **Amazon API Gateway** | Exposes the Relay REST API |
| **AWS Lambda** | Runs the API and delivery logic |
| **Amazon SQS** | Queues notifications for asynchronous processing |
| **Amazon DynamoDB** | Stores notification state and delivery information |
| **Amazon SES** | Delivers email notifications |
| **AWS IAM** | Controls permissions between services |
| **AWS CloudFormation / SAM** | Defines and deploys the infrastructure |

## Project Structure

```text
relay/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── create_event.py
│   │   └── get_event.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── notification.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── events.py
│   │   └── queue.py
│   │
│   ├── worker/
│   │   ├── __init__.py
│   │   └── deliver_notification.py
│   │
│   └── __init__.py
│
├── tests/
│   ├── __init__.py
│   ├── test_create_event.py
│   ├── test_delivery.py
│   └── test_get_event.py
│
├── infrastructure/
│   └── template.yaml
│
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Technologies

### Application

- Python
- boto3
- pytest

### AWS

- AWS Lambda
- Amazon API Gateway
- Amazon SQS
- Amazon DynamoDB
- Amazon Simple Email Service (SES)
- AWS IAM
- AWS CloudFormation
- AWS Serverless Application Model (SAM)

## Local Setup

Clone the repository:

```bash
git clone <repository-url>
cd relay
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows using Git Bash:

```bash
source .venv/Scripts/activate
```

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

## Testing

Relay's AWS integrations are mocked during unit testing, allowing the application logic to be tested without creating real cloud resources or sending real emails.

Run the complete test suite with:

```bash
pytest -v
```

The tests cover:

- successful notification creation;
- missing request fields;
- invalid JSON;
- retrieval of existing events;
- requests for nonexistent events;
- missing event IDs;
- successful email delivery;
- failed email delivery; and
- empty SQS events.

## Deployment

Relay's infrastructure is defined in:

```text
infrastructure/template.yaml
```

rather than requiring each AWS resource to be manually created.

### Prerequisites

Deployment requires:

- an AWS account;
- AWS CLI;
- AWS SAM CLI;
- authenticated AWS CLI access; and
- an email identity verified with Amazon SES.

The SES identity must be verified in the AWS region in which Relay is deployed.

### Validate

Validate the SAM template:

```bash
sam validate --template-file infrastructure/template.yaml
```

### Build

Build the application:

```bash
sam build --template-file infrastructure/template.yaml
```

### Deploy

Deploy using SAM:

```bash
sam deploy --guided --template-file .aws-sam/build/template.yaml
```

During guided deployment, provide:

- a stack name;
- an AWS region;
- the verified SES source email address; and
- permission for SAM to create the required IAM roles.

SAM creates the required resources automatically, including:

```text
API Gateway
    |
    +-- Create Event Lambda
    |
    +-- Get Event Lambda

DynamoDB
SQS
Delivery Lambda
IAM roles and policies
```

The deployed API URL is returned as a CloudFormation output after deployment.

## Example Usage

Once deployed, submit a notification with:

```bash
curl -X POST "https://<api-id>.execute-api.<region>.amazonaws.com/prod/events" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "subject": "Relay test",
    "message": "Hello from Relay."
  }'
```

Relay immediately returns the generated event ID and queued status.

The notification can subsequently be queried using:

```bash
curl "https://<api-id>.execute-api.<region>.amazonaws.com/prod/events/<event_id>"
```

Once processing has completed, the event status will report:

```json
{
  "status": "delivered"
}
```

## SES Sandbox

New Amazon SES accounts typically begin in the SES sandbox.

While operating in the sandbox, email sending is restricted and recipient addresses may also need to be verified with SES. This is sufficient for development and demonstration deployments of Relay.

Production use would require appropriate SES production access and additional API security.

## Security

The SAM template grants each Lambda function only the AWS permissions required for its role.

For example:

- the Create Event Lambda can write event information and send SQS messages;
- the Get Event Lambda only requires read access to event information; and
- the Delivery Lambda can update event state and send email through SES.

The example API itself does not implement client authentication. A production deployment should therefore protect the API using an appropriate authentication or authorization mechanism rather than exposing an unrestricted email-sending endpoint publicly.
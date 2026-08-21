from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Notification:
    recipient: str
    subject: str
    message: str
    event_id: str
    status: str
    created_at: str

    @classmethod
    def create(
        cls,
        recipient: str,
        subject: str,
        message: str,
    ) -> "Notification":
        return cls(
            recipient=recipient,
            subject=subject,
            message=message,
            event_id=str(uuid4()),
            status="queued",
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict:
        return asdict(self)
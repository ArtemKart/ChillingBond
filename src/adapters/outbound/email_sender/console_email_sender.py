import logging
from datetime import datetime

from src.domain.ports.services.email_sender import EmailSender

logger = logging.getLogger(__name__)


class ConsoleEmailSender(EmailSender):
    """
    Mock implementation EmailSender for development.
    Log into a console instead of sending email.
    """

    async def send_welcome_email(self, email: str) -> None:
        logger.info(
            "📧 [MOCK EMAIL] Welcome email would be sent",
            extra={
                "recipient": "email",
                "subject": "Welcome to ChillingBond!",
                "body": "Thank you for registering...",
            },
        )

        print(f"\n{'=' * 60}")
        print("📧 MOCK EMAIL SENT")
        print(f"To: {email}")
        print("Subject: Welcome to ChillingBond!")
        print("Body: Thank you for registering. Start managing your portfolio!")
        print(f"{'=' * 60}\n")

    async def send_bondholder_deleted_info_email(
        self, email: str, occurred_at: datetime
    ) -> None:
        logger.info(
            "📧 [MOCK EMAIL] Information email would be sent",
            extra={
                "recipient": "email",
                "subject": "Welcome to ChillingBond!",
            },
        )

        print(f"\n{'=' * 60}")
        print("📧 MOCK EMAIL SENT")
        print(f"To: {email}")
        print("Subject: You've deleted your bonds")
        print("Body: Bond Purchase Record Deleted!")
        print(f"{'=' * 60}\n")

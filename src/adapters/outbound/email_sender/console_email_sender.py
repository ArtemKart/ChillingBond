from datetime import datetime

from src.domain.services.email_sender import EmailSender


class ConsoleEmailSender(EmailSender):
    """
    Mock implementation EmailSender for development.
    Log into a console instead of sending email.
    """

    async def send_welcome_email(self, email: str) -> None:
        # logger.info(
        #     "📧 [MOCK EMAIL] Welcome email would be sent",
        #     recipient=email,
        #     subject="Welcome to ChillingBond!",
        #     body="Thank you for registering...",
        # )

        print(f"\n{'=' * 60}")
        print(f"📧 MOCK EMAIL SENT")
        print(f"To: {email}")
        print(f"Subject: Welcome to ChillingBond!")
        print(f"Body: Thank you for registering. Start managing your portfolio!")
        print(f"{'=' * 60}\n")

    async def send_bondholder_deleted_info_email(self, email: str, occurred_at: datetime) -> None:
        # logger.info(
        #     "📧 [MOCK EMAIL] Information email would be sent",
        #     recipient=email,
        #     subject="You've deleted your bonds",\
        # )

        print(f"\n{'=' * 60}")
        print(f"📧 MOCK EMAIL SENT")
        print(f"To: {email}")
        print(f"Subject: You've deleted your bonds")
        print(f"Body: Bond Purchase Record Deleted!")
        print(f"{'=' * 60}\n")

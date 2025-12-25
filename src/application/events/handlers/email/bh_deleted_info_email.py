import logging

from src.domain.events.bondholder_events import BondHolderDeletedEvent
from src.domain.ports.services.email_sender import EmailSender


logger = logging.getLogger(__name__)


class BondHolderDeletedEmailHandler:
    """Sends email notification when bondholder is deleted."""

    def __init__(
        self,
        email_sender: EmailSender,
    ) -> None:
        self._email_sender: EmailSender = email_sender

    async def handle(self, event: BondHolderDeletedEvent) -> None:
        logger.info(
            "Sending notification email",
            extra={"user_id": event.user_id, "email": event.email},
        )

        try:
            await self._email_sender.send_bondholder_deleted_info_email(
                email=event.email, occurred_at=event.occurred_at
            )
            logger.info(
                "Notification email sent successfully",
                extra={"user_id": event.user_id, "email": event.email},
            )
        except Exception as e:
            logger.error(
                "Failed to send welcome email",
                extra={"user_id": event.user_id, "email": event.email, "error": str(e)},
            )

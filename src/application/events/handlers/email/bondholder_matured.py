import logging

from src.domain.events.bondholder_events import BondHolderMatured
from src.domain.services.email_sender import EmailSender

logger = logging.getLogger(__name__)


class BondHolderMaturedEmailnHandler:
    """
    Event handler: send email notification when bondholder matures.
    """

    def __init__(self, email_sender: EmailSender) -> None:
        self._email_sender = email_sender

    async def handle(self, event: BondHolderMatured) -> None:
        """
        Send maturity notification email to the user.

        Args:
            event: BondHolderMatured event
        """
        logger.info(
            "Sending bondholder maturity notification",
            extra={
                "bondholder_id": str(event.bondholder_id),
                "user_id": str(event.user_id),
                "bond_id": str(event.bond_id),
            },
        )
        try:
            await self._email_sender.send_bondholder_matured_email(
                email=event.user_email,
                bond_series=event.bond_series,
                purchase_date=event.purchase_date,
            )

            logger.info(
                "Bondholder maturity notification sent successfully",
                extra={"user_id": str(event.user_id), "email": event.user_email},
            )
        except Exception as e:
            logger.error(
                "Failed to send bondholder maturity notification",
                exc_info=True,
                extra={
                    "user_id": str(event.user_id),
                    "email": event.user_email,
                    "error": str(e),
                },
            )

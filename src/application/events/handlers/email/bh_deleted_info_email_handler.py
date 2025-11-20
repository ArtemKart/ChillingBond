from src.domain.events.bondholder_events import BondHolderDeleted
from src.domain.services.email_sender import EmailSender


class BondHolderDeletedEmailHandler:
    """Sends email notification when bondholder is deleted."""

    def __init__(
        self,
        email_sender: EmailSender,
    ) -> None:
        self._email_sender = email_sender

    async def handle(self, event: BondHolderDeleted) -> None:
        # logger.info(
        #     "Sending notification email",
        #     user_id=event.user_id,
        #     email=event.email,
        # )

        try:
            await self._email_sender.send_bondholder_deleted_info_email(event)
            # logger.info(
            #     "Welcome email sent successfully",
            #     user_id=event.user_id,
            #     email=event.email,
            # )
        except Exception as _:
            # logger.error(
            #     "Failed to send welcome email",
            #     user_id=event.user_id,
            #     email=event.email,
            #     error=str(e),
            #     exc_info=True,
            # )
            pass

import os

from src.adapters.outbound.email_sender.console_email_sender import ConsoleEmailSender
from src.adapters.outbound.email_sender.smtp_email_sender import SMTPEmailSender
from src.application.events.handlers.email.bh_deleted_info import (
    BondHolderDeletedEmailHandler,
)
from src.application.events.handlers.email.bondholder_matured import BondHolderMaturedEmailnHandler
from src.application.events.handlers.email.welcome_email import (
    SendWelcomeEmailHandler,
)
from src.application.events.event_publisher import EventPublisher
from src.domain.events import UserCreated
from src.domain.events.bondholder_events import BondHolderDeletedEvent, BondHolderMatured
from src.domain.services.email_sender import EmailSender


def get_email_sender() -> EmailSender:
    """
    Fetch EmailSender implementation depending on the environment.

    Within development: ConsoleEmailSender (log only)
    Within production: SMTPEmailSender (send emails)
    """
    env = os.getenv("ENVIRONMENT", "dev")

    if env == "production":
        return SMTPEmailSender(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=os.getenv("SMTP_PORT", "587"),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("SMTP_FROM_EMAIL", "noreply@chillingbond.com"),
        )
    else:
        return ConsoleEmailSender()


def setup_event_publisher() -> EventPublisher:
    publisher = EventPublisher()
    email_sender = get_email_sender()
    welcome_email_handler = SendWelcomeEmailHandler(email_sender)
    bh_deleted_email_handler = BondHolderDeletedEmailHandler(email_sender)
    notification_handler = BondHolderMaturedEmailnHandler(
        email_sender=email_sender
    )
    
    publisher.subscribe(UserCreated, welcome_email_handler.handle)
    publisher.subscribe(BondHolderDeletedEvent, bh_deleted_email_handler.handle)
    publisher.subscribe(BondHolderMatured, notification_handler.handle)
    
    return publisher


_event_publisher: EventPublisher | None = None


def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = setup_event_publisher()
    return _event_publisher

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import smtplib

from src.adapters.outbound.email_sender.smtp_email_sender import SMTPEmailSender


@pytest.fixture
def smtp_config() -> dict[str, str | int]:
    """SMTP configuration for tests."""
    return {
        "smtp_host": "smtp.example.com",
        "smtp_port": "587",
        "smtp_user": "user@example.com",
        "smtp_password": "secret_password",
        "from_email": "noreply@chillingbond.com",
    }


@pytest.fixture
def email_sender(smtp_config: dict[str, str]) -> SMTPEmailSender:
    """Create SMTPEmailSender instance."""
    return SMTPEmailSender(**smtp_config)


@pytest.fixture
def mock_smtp_server() -> Mock:
    """Mock SMTP server."""
    server = Mock()
    server.starttls = Mock()
    server.login = Mock()
    server.sendmail = Mock()
    server.__enter__ = Mock(return_value=server)
    server.__exit__ = Mock(return_value=False)
    return server


async def test_send_welcome_email_success(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test successful welcome email sending."""
    recipient = "newuser@example.com"

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        await email_sender.send_welcome_email(recipient)

    mock_smtp_server.starttls.assert_called_once()
    mock_smtp_server.login.assert_called_once_with(
        "user@example.com", "secret_password"
    )
    mock_smtp_server.sendmail.assert_called_once()

    call_args = mock_smtp_server.sendmail.call_args[0]
    assert call_args[0] == "noreply@chillingbond.com"
    assert call_args[1] == recipient
    assert "Welcome to ChillingBond!" in call_args[2]


async def test_send_welcome_email_contains_correct_content(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test welcome email contains expected content."""
    recipient = "newuser@example.com"

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        await email_sender.send_welcome_email(recipient)

    message_content = mock_smtp_server.sendmail.call_args[0][2]

    assert "Subject: Welcome to ChillingBond!" in message_content
    assert f"To: {recipient}" in message_content
    assert "Thank you for registering" in message_content


async def test_send_welcome_email_smtp_exception(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test welcome email sending with SMTP exception."""
    recipient = "newuser@example.com"
    mock_smtp_server.sendmail.side_effect = smtplib.SMTPException("SMTP error")

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        with pytest.raises(smtplib.SMTPException, match="SMTP error"):
            await email_sender.send_welcome_email(recipient)


async def test_send_bondholder_deleted_info_email_success(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test successful bondholder deleted info email sending."""
    recipient = "user@example.com"
    occurred_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        await email_sender.send_bondholder_deleted_info_email(recipient, occurred_at)

    mock_smtp_server.starttls.assert_called_once()
    mock_smtp_server.login.assert_called_once_with(
        "user@example.com", "secret_password"
    )
    mock_smtp_server.sendmail.assert_called_once()

    call_args = mock_smtp_server.sendmail.call_args[0]
    assert call_args[0] == "noreply@chillingbond.com"
    assert call_args[1] == recipient


async def test_send_bondholder_deleted_info_email_contains_correct_content(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test bondholder deleted email contains expected content."""
    recipient = "user@example.com"
    occurred_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        await email_sender.send_bondholder_deleted_info_email(recipient, occurred_at)

    message_content = mock_smtp_server.sendmail.call_args[0][2]

    assert "Subject: You've deleted your bonds" in message_content
    assert f"To: {recipient}" in message_content
    assert "2024-01-15 10:30:00 UTC" in message_content
    assert "contact our support immediately" in message_content


async def test_send_bondholder_deleted_info_email_smtp_exception(
    email_sender: SMTPEmailSender,
    mock_smtp_server: Mock,
) -> None:
    """Test bondholder deleted email sending with SMTP exception."""
    recipient = "user@example.com"
    occurred_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    mock_smtp_server.sendmail.side_effect = smtplib.SMTPException("SMTP error")

    with patch("smtplib.SMTP", return_value=mock_smtp_server):
        with pytest.raises(smtplib.SMTPException, match="SMTP error"):
            await email_sender.send_bondholder_deleted_info_email(
                recipient, occurred_at
            )

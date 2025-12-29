import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.domain.ports.services.email_sender import EmailSender

logger = logging.getLogger(__name__)


class SMTPEmailSender(EmailSender):
    """Implementation EmailSender using SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: str,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = int(smtp_port)
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_email = from_email

    async def _send_email(
        self, to_email: str, subject: str, text_content: str, html_content: str
    ) -> None:
        """Send email via SMTP with both text and HTML parts."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._from_email
        message["To"] = to_email

        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_email, to_email, message.as_string())
            logger.info("Email sent via SMTP", extra={"recipient": to_email})
        except smtplib.SMTPException as e:
            logger.error(
                "SMTP error",
                extra={"recipient": to_email, "error": str(e)},
            )
            raise
        except Exception as e:
            logger.error(
                "Failed to send email",
                extra={"recipient": to_email, "error": str(e)},
            )
            raise

    async def send_welcome_email(self, email: str) -> None:
        text = """
            Welcome to ChillingBond!

            Thank you for registering. Start managing your bond portfolio today!

            Best regards,
            ChillingBond Team
        """

        html = """
            <html>
              <body>
                <h1>Welcome to ChillingBond!</h1>
                <p>Thank you for registering. Start managing your bond portfolio today!</p>
                <p>Best regards,<br>ChillingBond Team</p>
              </body>
            </html>
        """

        await self._send_email(email, "Welcome to ChillingBond!", text, html)

    async def send_bondholder_deleted_info_email(
        self, email: str, occurred_at: datetime
    ) -> None:
        deletion_time = occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        text = f"""
            Bond Purchase Record Deleted

            Your bond purchase record has been successfully removed from your portfolio.

            Deletion Time: {deletion_time}

            If you did not perform this action, please contact our support immediately.

            Best regards,
            ChillingBond Team
        """

        html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h1 style="color: #2c3e50;">Bond Purchase Record Deleted</h1>
                <p>Your bond purchase record has been successfully removed from your portfolio.</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                  <p style="margin: 5px 0;"><strong>Deletion Time:</strong> {deletion_time}</p>
                </div>

                <p style="color: #e74c3c; font-weight: bold;">
                  ⚠️ If you did not perform this action, please contact our support immediately.
                </p>

                <p style="margin-top: 30px;">
                  Best regards,<br>
                  <strong>ChillingBond Team</strong>
                </p>
              </body>
            </html>
        """

        await self._send_email(email, "You've deleted your bonds", text, html)

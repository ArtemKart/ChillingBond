import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.domain.services.email_sender import EmailSender

logger = logging.getLogger(__name__)


class SMTPEmailSender(EmailSender):
    """Implementation EmailSender using SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_email = from_email

    async def send_welcome_email(self, email: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Welcome to ChillingBond!"
        message["From"] = self._from_email
        message["To"] = email

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

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_email, email, message.as_string())
            logger.info(
                "Email sent via SMTP",
                extra={"recipient": email},
            )
        except smtplib.SMTPException as e:
            logger.error(
                "SMTP error",
                extra={"recipient": email, "error": str(e)},
            )
            raise
        except Exception as e:
            logger.error(
                "Failed to send email",
                extra={"recipient": email, "error": str(e)},
            )
            raise

    async def send_bondholder_deleted_info_email(
        self, email: str, occurred_at: datetime
    ) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = "You've deleted your bonds"
        message["From"] = self._from_email
        message["To"] = email

        text = f"""
            Bond Purchase Record Deleted
    
            Your bond purchase record has been successfully removed from your portfolio.

            Deletion Time: {occurred_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
    
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
                  <p style="margin: 5px 0;"><strong>Deletion Time:</strong> {occurred_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
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

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_email, email, message.as_string())
            logger.info(
                "Email sent via SMTP",
                extra={"recipient": email},
            )
        except smtplib.SMTPException as e:
            logger.error(
                "SMTP error",
                extra={"recipient": email, "error": str(e)},
            )
            raise
        except Exception as e:
            logger.error(
                "Failed to send email",
                extra={"recipient": email, "error": str(e)},
            )
            raise

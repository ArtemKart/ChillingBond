from abc import ABC, abstractmethod
from datetime import date, datetime


class EmailSender(ABC):
    @abstractmethod
    async def send_welcome_email(self, email: str) -> None:
        """
        Send welcome email to new user.

        Args:
            email: User email address
        """
        pass

    @abstractmethod
    async def send_bondholder_deleted_info_email(
        self, email: str, occurred_at: datetime
    ) -> None:
        """
        Send informational email when bondholder deleted.

        Args:
            email: User email address
            occurred_at: Date when bondholder was deleted
        """
        pass

    @abstractmethod
    async def send_bondholder_matured_email(
        self, email: str, bond_series: str, purchase_date: date
    ) -> None:
        """
        Send informational email when bondholder matured.

        Args:
            email: User email address
            bond_series: Bond series
            purchase_date: Date when bondholder was purchased
        """
        pass

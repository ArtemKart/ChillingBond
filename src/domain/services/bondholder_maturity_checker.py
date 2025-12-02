from datetime import date

from dateutil.relativedelta import relativedelta

from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder


class BondHolderMaturityChecker:
    """Domain service for bondholder maturity checker"""

    def is_matured(self, bondholder: BondHolder, bond: Bond, current_date: date) -> bool:
        """
        Check if bondholder maturity is matured

        Args:
            bondholder: Bondholder object
            bond: Bond object
            current_date: Current date

        Returns:
            True if bondholder is matured, False otherwise
        """

        maturity_date = self._calculate_maturity_date(
            bondholder.purchase_date, bond.maturity_period
        )
        return current_date >= maturity_date

    @staticmethod
    def _calculate_maturity_date(purchase_date: date, maturity_period: int) -> date:
        """
        Calculate maturity date

        Args:
            purchase_date: Purchase date
            maturity_period: Maturity period in months

        Returns:
            Maturity date
        """
        return purchase_date + relativedelta(months=maturity_period)

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from dateutil.relativedelta import relativedelta

from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder
from src.domain.entities.reference_rate import ReferenceRate


class BondHolderIncomeCalculator:
    """Domain service for bondholder income calculator"""

    def __init__(self, bondholder: BondHolder, bond: Bond) -> None:
        self._bondholder = bondholder
        self._bond = bond

    def calculate_month_bondholder_income(
        self,
        reference_rate: ReferenceRate,
        day: datetime = datetime.today(),
    ) -> Decimal:
        """
        Calculate monthly income for a bondholder.

        Determines whether to use the initial fixed interest rate (first period)
        or the variable reference rate (subsequent periods) based on the payment date.

        Args:
            reference_rate: Current reference rate from the central bank
            day: Payment date for income calculation (defaults to today)

        Returns:
            Net monthly income after tax for all bonds held by the bondholder
        """
        interest_period_end = self._bondholder.purchase_date + relativedelta(
            months=self._bond.first_interest_period
        )
        days_in_period = self._days_in_period(
            purchase_date=self._bondholder.purchase_date
        )

        if day.date() >= interest_period_end.date():
            return self._calculate_regular_income(
                reference_rate=reference_rate.value,
                days_in_month=days_in_period,
            )
        return self._calculate_interest_income(
            days_in_month=days_in_period,
        )

    def _calculate_interest_income(
        self,
        days_in_month: int,
    ) -> Decimal:
        """
        Calculate income for the first interest period with a fixed rate.

        Uses the initial fixed interest rate specified in the bond terms.
        Formula: (nominal * rate / 365 * days) * (1 - tax) * quantity

        Args:
            days_in_month: Number of days in the interest period

        Returns:
            Total net income after 19% tax (Belka tax) for all bonds
        """
        daily_rate = (
            self._bond.nominal_value
            * self._from_percent(self._bond.initial_interest_rate)
            * days_in_month
            / Decimal("365")
        )
        gross_interest = daily_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net_interest = gross_interest * (Decimal("1") - Decimal("0.19"))

        return net_interest * self._bondholder.quantity

    def _calculate_regular_income(
        self,
        reference_rate: Decimal,
        days_in_month: int,
    ) -> Decimal:
        """
        Calculate income for subsequent periods with a variable rate.

        Uses the reference rate (typically NBP rate) plus margin.
        Formula: (nominal * (ref_rate + margin) / 365 * days) * (1 - tax) * quantity

        Args:
            reference_rate: Variable reference rate as percentage (e.g., 4.75 for 4.75%)
            days_in_month: Number of days in the interest period

        Returns:
            Total net income after 19% tax (Belka tax) for all bonds
        """
        annual_rate = self._from_percent(reference_rate) + self._from_percent(
            self._bond.reference_rate_margin
        )
        gross_interest_per_bond = (
            self._bond.nominal_value * annual_rate * days_in_month / Decimal("365")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return gross_interest_per_bond * Decimal("0.81") * self._bondholder.quantity

    @staticmethod
    def _from_percent(percent: Decimal) -> Decimal:
        """
        Convert percentage to decimal fraction.

        Args:
            percent: Percentage value (e.g., 5.00 for 5%)

        Returns:
            Decimal fraction (e.g., 0.05 for 5%)
        """
        return percent / Decimal(100)

    @staticmethod
    def _days_in_period(purchase_date: datetime, today: datetime | None = None) -> int:
        """
        Calculate the number of days in the current interest period.

        Interest periods run monthly from the purchase day. For example, if purchased
        on the 2nd, periods are: 2nd of month N to 2nd of month N+1.

        Args:
            purchase_date: Date when bonds were purchased
            today: Current date for calculation (defaults to today)

        Returns:
            Number of days in the current interest period (typically 28-31 days)
        """
        if not today:
            today = datetime.today()
        purchase_day = purchase_date.day
        period_start = datetime(purchase_date.year, purchase_date.month, purchase_day)

        while period_start <= today:
            period_end = period_start + relativedelta(months=1)
            if period_start <= today < period_end:
                return (period_end - period_start).days
            period_start = period_end
        period_end = period_start
        period_start = period_start - relativedelta(months=1)

        return (period_end - period_start).days

    def calculate_bondholder_income_for_period(
        self,
        reference_rates: list[ReferenceRate],
        start_date: datetime,
        end_date: datetime,
    ) -> dict[datetime, Decimal]:
        """
        Calculate monthly income for a bondholder across a date range.

        Args:
            reference_rates: List of reference rates with their start dates
            start_date: Start of the calculation period (inclusive)
            end_date: End of the calculation period (inclusive)

        Returns:
            Dictionary mapping payment dates to net income amounts
        """
        result: dict[datetime, Decimal] = {}

        sorted_rates = sorted(reference_rates, key=lambda r: r.start_date)
        current_payment_date = self._bondholder.purchase_date + relativedelta(months=1)

        while current_payment_date <= end_date:
            if current_payment_date >= start_date:
                applicable_rate = None
                for rate in reversed(sorted_rates):
                    if rate.start_date <= current_payment_date:
                        applicable_rate = rate
                        break

                if applicable_rate is None:
                    raise ValueError(
                        f"No reference rate found for payment date {current_payment_date}"
                    )
                income = self.calculate_month_bondholder_income(
                    reference_rate=applicable_rate,
                    day=current_payment_date,
                )
                result[current_payment_date] = income
            current_payment_date += relativedelta(months=1)

        return result

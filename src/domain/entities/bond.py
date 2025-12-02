from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


@dataclass
class Bond:
    """Represents the bondholder

    Args:
        id (UUID): Bond identifier.
        nominal_value (float): Nominal value of a single bondholder unit.
        series (str): Identifier or code representing the bondholder series.
        maturity_period (int): Total lifetime of the bondholder, typically expressed
            in months.
        initial_interest_rate (float): Interest rate applied during the initial
            period of the bondholder.
        first_interest_period (int): Duration of the initial interest rate period,
            typically expressed in months.
        reference_rate_margin (float): Additional percentage added to the reference rate (spread).
    """

    id: UUID
    series: str
    nominal_value: Decimal
    maturity_period: int
    initial_interest_rate: Decimal
    first_interest_period: int
    reference_rate_margin: Decimal

    @classmethod
    def create(
        cls,
        series: str,
        nominal_value: float,
        maturity_period: int,
        initial_interest_rate: float,
        first_interest_period: int,
        reference_rate_margin: float,
    ) -> "Bond":
        bond = Bond(
            id=uuid4(),
            series=series,
            nominal_value=nominal_value,
            maturity_period=maturity_period,
            initial_interest_rate=initial_interest_rate,
            first_interest_period=first_interest_period,
            reference_rate_margin=reference_rate_margin,
        )
        bond.validate()
        return bond

    def validate(self) -> None:
        self._validate_nominal_value()
        self._validate_maturity_period()
        self._validate_initial_interest_rate()

    def _validate_nominal_value(self) -> None:
        if self.nominal_value <= 0:
            raise ValidationError("Bond nominal_value must be greater than 0.")

    def _validate_maturity_period(self) -> None:
        if self.maturity_period <= 0:
            raise ValidationError("Bond maturity_period must be greater than 0.")

    def _validate_initial_interest_rate(self) -> None:
        if self.initial_interest_rate <= 0:
            raise ValidationError("Bond initial_interest_rate must be greater than 0.")

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4


@dataclass
class ReferenceRate:
    """
    Entity represents reference rate data used in floating-rate bond calculations.

    A reference rate represents a country's key interest rate that serves as the benchmark
    for calculating floating-rate bond yields. For Polish bonds, this is the reference rate
    published by Narodowy Bank Polski (NBP).

    Each reference rate is valid for a specific time period, which may vary in duration.
    The repository handles retrieving rates for specific dates and managing the temporal
    nature of these benchmark values.

    Note:
        Reference rates are distinct from coupon rates - they serve as the base rate
        to which a spread/margin is added to calculate the actual coupon payment
        for floating-rate bonds.

    Args:
        id (UUID): Reference rate identifier.
        value (float): Reference rate value.
        start_date (datetime): Date from which the reference rate becomes effective.
        end_date (datetime): Date until which the reference rate is valid.
            Can be None if it is still in effect.
    """

    id: UUID
    value: Decimal
    start_date: date
    end_date: date | None = None

    @classmethod
    def create(
        cls,
        value: Decimal,
        start_date: date,
        end_date: date | None = None,
    ) -> Self:
        ref_rate = cls(
            id=uuid4(),
            value=value,
            start_date=start_date,
            end_date=end_date,
        )
        ref_rate.validate()
        return ref_rate

    def validate(self) -> None:
        self._validate_ref_rate_value()

    def _validate_ref_rate_value(self) -> None:
        if not isinstance(self.value, Decimal):
            raise TypeError("Reference rate value must be a Decimal.")
        if self.value < Decimal("0.0"):
            raise ValueError("Reference rate value cannot be negative.")

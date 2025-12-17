from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


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

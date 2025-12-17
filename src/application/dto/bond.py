from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal


@dataclass
class BondDTO:
    id: UUID
    nominal_value: Decimal
    series: str
    maturity_period: int
    initial_interest_rate: Decimal
    first_interest_period: int
    reference_rate_margin: Decimal


@dataclass
class BondCreateDTO:
    series: str
    nominal_value: Decimal
    maturity_period: int
    initial_interest_rate: Decimal
    first_interest_period: int
    reference_rate_margin: Decimal


@dataclass
class BondUpdateDTO:
    nominal_value: Decimal | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: Decimal | None = None
    first_interest_period: int | None = None
    reference_rate_margin: Decimal | None = None

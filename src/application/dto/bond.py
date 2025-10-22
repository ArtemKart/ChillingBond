from dataclasses import dataclass
from uuid import UUID


@dataclass
class BondDTO:
    id: UUID
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float


@dataclass
class BondCreateDTO:
    series: str
    nominal_value: float
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float


@dataclass
class BondUpdateDTO:
    nominal_value: float | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: float | None = None
    first_interest_period: int | None = None
    reference_rate_margin: float | None = None

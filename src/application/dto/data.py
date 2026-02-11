from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class EquityDTO:
    data: list[tuple[date, Decimal]]

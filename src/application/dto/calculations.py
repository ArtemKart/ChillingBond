from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MonthlyIncomeResponseDTO:
    data: dict[UUID, Decimal]

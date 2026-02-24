from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class MonthIncomeResponse(BaseModel):
    data: dict[UUID, Decimal]

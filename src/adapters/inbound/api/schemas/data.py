
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class EquityResponse(BaseModel):
    equity: list[tuple[date, Decimal]]

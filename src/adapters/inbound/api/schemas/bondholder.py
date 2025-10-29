from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field

from .bond import BondBase


class BondHolderResponse(BondBase):
    id: UUID
    quantity: int = Field(..., gt=0, description="Number of bonds")
    purchase_date: date
    last_update: datetime | None = None
    bond_id: UUID


class BondHolderChangeRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity to change")
    is_positive: bool


class BondHolderCreateRequest(BondBase):
    quantity: int = Field(..., gt=0, description="Number of bonds")
    purchase_date: date

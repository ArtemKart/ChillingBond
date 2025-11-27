from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field

from src.adapters.inbound.api.schemas.bond import BondBase


class BondHolderResponse(BondBase):
    id: UUID
    quantity: int = Field(..., gt=0, description="Number of bonds")
    purchase_date: date
    last_update: datetime | None = None
    bond_id: UUID


class BondHolderChangeRequest(BaseModel):
    new_quantity: int = Field(..., gt=0, description="New quantity")


class BondHolderCreateRequest(BondBase):
    quantity: int = Field(..., gt=0, description="Number of bonds")
    purchase_date: date

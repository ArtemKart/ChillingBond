from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from src.adapters.outbound.database.base import Base


class User(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str | None] = mapped_column(String(15), nullable=True)


class Bond(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    nominal_value: Mapped[Decimal]
    series: Mapped[str] = mapped_column(unique=True, index=True)
    maturity_period: Mapped[int]
    initial_interest_rate: Mapped[Decimal]
    first_interest_period: Mapped[int]
    reference_rate_margin: Mapped[Decimal]


class BondHolder(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    bond_id: Mapped[UUID] = mapped_column(ForeignKey("bond.id"))
    quantity: Mapped[int]
    purchase_date: Mapped[date]
    last_update: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class ReferenceRate(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    value: Mapped[Decimal]
    start_date: Mapped[date]
    end_date: Mapped[date | None] = mapped_column(nullable=True)

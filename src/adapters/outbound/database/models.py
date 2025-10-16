from datetime import datetime
from uuid import UUID

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from src.adapters.outbound.database.base import Base


class User(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str | None] = mapped_column(String(15), nullable=True)


class Bond(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    buy_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    nominal_value: Mapped[float]
    series: Mapped[str]
    maturity_period: Mapped[int]
    initial_interest_rate: Mapped[float]
    first_interest_period: Mapped[int]
    reference_rate_margin: Mapped[float]
    last_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class ReferenceRate(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    value: Mapped[float]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime | None] = mapped_column(nullable=True)

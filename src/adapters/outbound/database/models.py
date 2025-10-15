from datetime import datetime
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from src.adapters.outbound.database.base import Base


class User(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str]
    password: Mapped[str]
    name: Mapped[str | None] = mapped_column(String(15), nullable=True)


class Bond(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    nominal_value: Mapped[float]
    series: Mapped[str]
    maturity_period: Mapped[int]
    initial_interest_rate: Mapped[float]
    first_interest_period: Mapped[int]
    reference_rate_margin: Mapped[float]


class ReferenceRate(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    value: Mapped[float]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime | None] = mapped_column(nullable=True)

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.adapters.inbound.api.main import app
from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import BondHolder as BondholderModel
from src.application.dto.user import UserDTO


@pytest_asyncio.fixture
async def multiple_bondholders(
    t_session: AsyncSession, t_current_user: UserDTO, t_bond: BondModel
) -> list[BondholderModel]:
    n = 3
    bhs = [
        BondholderModel(
            id=uuid4(),
            user_id=t_current_user.id,
            bond_id=t_bond.id,
            quantity=10 * (i + 1),
            purchase_date=date.today(),
            last_update=None,
        )
        for i in range(n)
    ]
    t_session.add_all(bhs)
    await t_session.commit()
    [await t_session.refresh(bhs[i]) for i in range(n)]
    return bhs


async def test_success_with_multiple_bonds(
    client: AsyncClient,
    multiple_bondholders: list[BondholderModel],
    t_bond: BondModel,
) -> None:

    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert isinstance(data, list)
    assert len(data) == 3

    for i, bh in enumerate(multiple_bondholders):
        assert data[i]["id"] == str(bh.id)
        assert data[i]["bond_id"] == str(bh.bond_id)
        assert data[i]["quantity"] == bh.quantity
        assert data[0]["series"] == t_bond.series
        assert data[0]["purchase_date"] == bh.purchase_date.isoformat()
        assert data[0]["nominal_value"] == t_bond.nominal_value
        assert data[0]["maturity_period"] == t_bond.maturity_period
        assert data[0]["initial_interest_rate"] == t_bond.initial_interest_rate
        assert data[0]["reference_rate_margin"] == t_bond.reference_rate_margin
        assert data[0]["first_interest_period"] == t_bond.first_interest_period


async def test_success_with_single_bond(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:

    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(t_bondholder.id)
    assert data[0]["quantity"] == 10
    assert data[0]["purchase_date"] == t_bondholder.purchase_date.isoformat()
    assert data[0]["bond_id"] == str(t_bondholder.bond_id)


async def test_empty_list(
    client: AsyncClient,
    t_session: AsyncSession,
    t_current_user: UserDTO,
) -> None:

    bhs = await t_session.execute(
        text("SELECT * FROM bondholder WHERE user_id = :t_current_user"),
        {"t_current_user": str(t_current_user.id)},
    )
    bhs = bhs.scalars().all()
    assert not bhs

    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert isinstance(data, list)
    assert len(data) == 0


async def test_unauthorized(client: AsyncClient) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)  # noqa

    r = await client.get("api/bonds")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


async def test_response_structure(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:

    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    required_fields = [
        "id",
        "quantity",
        "purchase_date",
        "last_update",
        "bond_id",
        "series",
        "nominal_value",
        "maturity_period",
        "initial_interest_rate",
        "first_interest_period",
        "reference_rate_margin",
    ]

    for field in required_fields:
        assert field in data[0]


async def test_decimal_precision(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_bond: BondModel,
) -> None:
    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert Decimal(data[0]["nominal_value"]).quantize(Decimal("0.01")) == Decimal(
        t_bond.nominal_value
    )
    assert Decimal(data[0]["initial_interest_rate"]).quantize(
        Decimal("0.01")
    ) == Decimal(t_bond.initial_interest_rate)
    assert Decimal(data[0]["reference_rate_margin"]).quantize(
        Decimal("0.01")
    ) == Decimal(t_bond.reference_rate_margin)


async def test_date_serialization(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:
    if not t_bondholder.last_update:
        t_bondholder.last_update = t_bondholder.purchase_date + timedelta(days=10)
        t_bondholder = await t_session.merge(t_bondholder)
        await t_session.commit()
        await t_session.refresh(t_bondholder)

    r = await client.get("api/bonds")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert data[0]["purchase_date"] == t_bondholder.purchase_date.isoformat()
    assert (
        data[0]["last_update"].replace("Z", "+00:00")
        == t_bondholder.last_update.isoformat()
    )

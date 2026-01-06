from datetime import timedelta
from uuid import uuid4

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.inbound.api.main import app
from src.adapters.outbound.database.models import BondHolder as BondholderModel
from src.adapters.outbound.database.models import Bond as BondModel


async def test_success(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:
    r = await client.get(f"api/bonds/{t_bondholder.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    bond = await t_session.get(BondModel, t_bondholder.bond_id)

    assert data["id"] == str(t_bondholder.id)
    assert data["quantity"] == t_bondholder.quantity
    assert data["purchase_date"] == t_bondholder.purchase_date.isoformat()
    if data["last_update"]:
        assert (
            data["last_update"].replace("Z", "+00:00")
            == t_bondholder.last_update.isoformat()
        )
    assert data["bond_id"] == str(t_bondholder.bond_id)
    assert data["series"] == bond.series
    assert data["nominal_value"] == bond.nominal_value
    assert data["maturity_period"] == bond.maturity_period
    assert data["initial_interest_rate"] == bond.initial_interest_rate
    assert data["first_interest_period"] == bond.first_interest_period
    assert data["reference_rate_margin"] == bond.reference_rate_margin


async def test_not_found(
    client: AsyncClient,
) -> None:
    r = await client.get(f"api/bonds/{uuid4()}")

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "BondHolder not found"


async def test_invalid_token(
    client: AsyncClient,
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)  # noqa

    r = await client.get(f"api/bonds/{uuid4()}")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == "Not authenticated"


async def test_invalid_uuid_format(
    client: AsyncClient,
) -> None:
    r = await client.get(f"api/bonds/not-a-valid-uuid")
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_response_structure(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:

    r = await client.get(f"api/bonds/{t_bondholder.id}")

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
        assert field in data


async def test_decimal_precision(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:

    r = await client.get(f"api/bonds/{t_bondholder.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    bond = await t_session.get(BondModel, t_bondholder.bond_id)
    assert data["nominal_value"] == float(bond.nominal_value)
    assert data["initial_interest_rate"] == float(bond.initial_interest_rate)
    assert data["reference_rate_margin"] == float(bond.reference_rate_margin)


async def test_date_serialization(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:
    last_update = t_bondholder.last_update

    if not last_update:
        t_bondholder.last_update = t_bondholder.purchase_date + timedelta(days=10)
        t_bondholder = await t_session.merge(t_bondholder)
        await t_session.commit()
        await t_session.refresh(t_bondholder)

    r = await client.get(f"api/bonds/{t_bondholder.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert data["purchase_date"] == t_bondholder.purchase_date.isoformat()
    assert (
        data["last_update"].replace("Z", "+00:00")
        == t_bondholder.last_update.isoformat()  # noqa
    )

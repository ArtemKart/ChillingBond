from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from adapters.outbound.repositories.bondholder import SQLAlchemyBondHolderRepository
from application.use_cases.bondholder.bh_update_quantity import (
    UpdateBondHolderQuantityUseCase,
)
from src.adapters.inbound.api.main import app
from src.adapters.outbound.database.models import BondHolder as BondholderModel


@pytest.fixture
def valid_json() -> dict[str, int]:
    return {
        "new_quantity": 5,
    }


@pytest.fixture
def use_case(
    bond_repo: SQLAlchemyBondRepository,
    bondholder_repo: SQLAlchemyBondHolderRepository,
) -> UpdateBondHolderQuantityUseCase:
    return UpdateBondHolderQuantityUseCase(
        bond_repo=bond_repo, bondholder_repo=bondholder_repo
    )


async def test_success(
    client: AsyncClient, t_session: AsyncSession, t_bondholder: BondholderModel
) -> None:
    valid_json = {"new_quantity": 100}
    assert valid_json["new_quantity"] != t_bondholder.quantity

    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity", json=valid_json
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(t_bondholder.id)
    assert data["quantity"] == valid_json["new_quantity"]

    bh = await t_session.get(BondholderModel, t_bondholder.id)
    assert bh.quantity == valid_json["new_quantity"]


async def test_invalid_purchase_id(
    client: AsyncClient,
    valid_json: dict[str, int],
) -> None:
    invalid_id = "not-a-valid-uuid"

    response = await client.patch(f"api/bonds/{invalid_id}/quantity", json=valid_json)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_unauthorized(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    valid_json: dict[str, int],
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)  # noqa

    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity", json=valid_json
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_bondholder_not_found(
    client: AsyncClient,
    use_case: UpdateBondHolderQuantityUseCase,
    valid_json: dict[str, int],
) -> None:
    response = await client.patch(f"api/bonds/{uuid4()}/quantity", json=valid_json)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Bond holder not found"


async def test_response_structure(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    valid_json: dict[str, int],
    use_case: UpdateBondHolderQuantityUseCase,
) -> None:
    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity", json=valid_json
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

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


async def test_last_update(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    valid_json: dict[str, int],
    use_case: UpdateBondHolderQuantityUseCase,
) -> None:
    old_last_update = t_bondholder.last_update

    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity", json=valid_json
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    new_last_update = data["last_update"]

    if not old_last_update:
        assert new_last_update is not None
    else:
        assert new_last_update > str(old_last_update)


async def test_invalid_json(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:
    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity",
        content="invalid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_wrong_data_types(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:
    invalid_json = {
        "quantity": "five",
    }

    response = await client.patch(
        f"api/bonds/{t_bondholder.id}/quantity", json=invalid_json
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

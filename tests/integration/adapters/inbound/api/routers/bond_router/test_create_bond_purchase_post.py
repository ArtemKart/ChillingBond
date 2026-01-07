from decimal import Decimal
from typing import Any

from datetime import date

import pytest
from fastapi import status
from httpx import AsyncClient

from adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from adapters.outbound.repositories.bondholder import SQLAlchemyBondHolderRepository
from application.use_cases.bondholder.bh_create import BondHolderCreateUseCase
from src.adapters.inbound.api.main import app


@pytest.fixture
def valid_bond_data() -> dict[str, Any]:
    # Object of type Decimal is not JSON serializable, so keep as float
    return {
        "quantity": 10,
        "purchase_date": date.today().isoformat(),
        "series": "ROR1206",
        "nominal_value": 100.00,
        "maturity_period": 12,
        "initial_interest_rate": 5.5,
        "first_interest_period": 3,
        "reference_rate_margin": 1.2,
    }


@pytest.fixture
def use_case(
    bond_repo: SQLAlchemyBondRepository, bondholder_repo: SQLAlchemyBondHolderRepository
) -> BondHolderCreateUseCase:
    return BondHolderCreateUseCase(
        bond_repo=bond_repo,
        bondholder_repo=bondholder_repo,
    )


async def test_success(
    client: AsyncClient,
    valid_bond_data: dict[str, Any],
    use_case: BondHolderCreateUseCase,
) -> None:
    r = await client.post("api/bonds", json=valid_bond_data)

    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()

    assert data["id"] is not None
    assert data["quantity"] == valid_bond_data["quantity"]
    assert data["purchase_date"] == valid_bond_data["purchase_date"]
    assert data["bond_id"] is not None
    assert data["series"] == valid_bond_data["series"]
    assert Decimal(data["nominal_value"]) == Decimal(valid_bond_data["nominal_value"])
    assert data["maturity_period"] == valid_bond_data["maturity_period"]
    assert Decimal(data["initial_interest_rate"]) == Decimal(
        valid_bond_data["initial_interest_rate"]
    )
    assert data["first_interest_period"] == valid_bond_data["first_interest_period"]
    assert Decimal(data["reference_rate_margin"]) == Decimal(
        valid_bond_data["reference_rate_margin"]
    )


async def test_missing_required_fields(
    client: AsyncClient,
) -> None:
    incomplete_data = {
        "quantity": 10,
        "series": "ROR1206",
        # Missing other required fields
    }
    r = await client.post("api/bonds", json=incomplete_data)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test__invalid_quantity(
    client: AsyncClient, valid_bond_data: dict[str, Any]
) -> None:

    valid_bond_data["quantity"] = -5
    r = await client.post("api/bonds", json=valid_bond_data)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_invalid_date_format(
    client: AsyncClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["purchase_date"] = "invalid-date"
    r = await client.post("api/bonds", json=valid_bond_data)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_invalid_nominal_value(
    client: AsyncClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["nominal_value"] = "-1000"
    r = await client.post("api/bonds", json=valid_bond_data)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_invalid_maturity_period(
    client: AsyncClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["maturity_period"] = 0
    r = await client.post("api/bonds", json=valid_bond_data)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_unauthorized(
    client: AsyncClient,
    valid_bond_data: dict[str, Any],
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)  # noqa

    r = await client.post("api/bonds", json=valid_bond_data)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

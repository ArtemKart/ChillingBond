from typing import Any
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.inbound.api.main import app
from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import BondHolder as BondHolderModel


@pytest.fixture
def partial_upd_request() -> dict[str, float]:
    return {
        "nominal_value": 2000.00,
        "initial_interest_rate": 7.0,
    }


@pytest.fixture
def valid_upd_json() -> dict[str, Any]:
    return {
        "nominal_value": 100.00,
        "series": "ROR1000",
        "maturity_period": 18,
        "initial_interest_rate": 6.5,
        "first_interest_period": 4,
        "reference_rate_margin": 1.5,
    }


async def test_success_full_update(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
    valid_upd_json: dict[str, Any],
    t_session: AsyncSession,
) -> None:
    bond = await t_session.get(BondModel, t_bondholder.bond_id)
    assert bond

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=valid_upd_json
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert data["nominal_value"] == float(bond.nominal_value)
    assert data["series"] == bond.series
    assert data["maturity_period"] == bond.maturity_period
    assert data["initial_interest_rate"] == float(bond.initial_interest_rate)
    assert data["first_interest_period"] == bond.first_interest_period
    assert data["reference_rate_margin"] == float(bond.reference_rate_margin)


async def test_success_partial_update(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
    t_session: AsyncSession,
    partial_upd_request: dict[str, float],
) -> None:

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=partial_upd_request
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert data["nominal_value"] == partial_upd_request["nominal_value"]
    assert data["initial_interest_rate"] == partial_upd_request["initial_interest_rate"]


async def test_bondholder_not_found(
    client: AsyncClient,
    valid_upd_json: dict[str, Any],
) -> None:
    r = await client.put(f"api/bonds/{uuid4()}/specification", json=valid_upd_json)

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "BondHolder not found"


async def test_invalid_uuid(
    client: AsyncClient,
    valid_upd_json: dict[str, Any],
) -> None:
    r = await client.put(
        "api/bonds/not-a-valid-uuid/specification", json=valid_upd_json
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_unauthorized(
    client: AsyncClient,
    partial_upd_request: dict[str, float],
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)  # noqa

    r = await client.put(f"api/bonds/{uuid4()}/specification", json=partial_upd_request)

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


async def test_missing_required_fields(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    r = await client.put(f"api/bonds/{t_bondholder.id}/specification", json={})

    assert r.status_code == status.HTTP_200_OK


async def test_invalid_nominal_value(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    invalid_request = {
        "nominal_value": -1000.00,
        "series": "ROR5555",
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=invalid_request
    )

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_invalid_maturity_period(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    invalid_request = {
        "nominal_value": 1000.00,
        "maturity_period": -12,
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=invalid_request
    )

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_update_bond_invalid_interest_rate(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    invalid_request = {
        "nominal_value": 1000.00,
        "initial_interest_rate": -5.5,
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=invalid_request
    )

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_response_structure(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
    valid_upd_json: dict[str, Any],
) -> None:

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=valid_upd_json
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    required_fields = [
        "nominal_value",
        "series",
        "maturity_period",
        "initial_interest_rate",
        "first_interest_period",
        "reference_rate_margin",
    ]
    for field in required_fields:
        assert field in data


async def test_decimal_precision(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    update_request = {
        "nominal_value": 1234.56,
        "initial_interest_rate": 7.25,
        "reference_rate_margin": 2.15,
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=update_request
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert data["nominal_value"] == 1234.56
    assert data["initial_interest_rate"] == 7.25
    assert data["reference_rate_margin"] == 2.15


async def test_different_series(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    series_list = ["ROR0000", "ROR1111", "ROR2222", "ROR3333"]

    for series in series_list:
        update_request = {
            "series": series,
            "nominal_value": 1000.00,
        }

        r = await client.put(
            f"api/bonds/{t_bondholder.id}/specification", json=update_request
        )

        assert r.status_code == status.HTTP_200_OK
        assert r.json()["series"] == series


async def test_invalid_json(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification",
        content="invalid json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_wrong_data_types(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    invalid_request = {
        "nominal_value": "one thousand",
        "maturity_period": "twelve months",
        "initial_interest_rate": "five percent",
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=invalid_request
    )

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_with_all_fields_as_none(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    update_request = {
        "nominal_value": None,
        "series": None,
        "maturity_period": None,
        "initial_interest_rate": None,
        "first_interest_period": None,
        "reference_rate_margin": None,
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=update_request
    )

    assert r.status_code == status.HTTP_200_OK


async def test_extra_fields_ignored(
    client: AsyncClient,
    t_bondholder: BondHolderModel,
) -> None:
    update_request = {
        "nominal_value": 1500.00,
        "series": "ROR1111",
        "extra_field": "should be ignored",
        "another_extra": 123,
    }

    r = await client.put(
        f"api/bonds/{t_bondholder.id}/specification", json=update_request
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "extra_field" not in data
    assert "another_extra" not in data

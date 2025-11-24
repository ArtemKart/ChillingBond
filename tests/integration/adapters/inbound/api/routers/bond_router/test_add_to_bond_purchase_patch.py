from typing import Any

from datetime import date, datetime, timezone, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock

import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient

from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
async def valid_purchase_id() -> UUID:
    return uuid4()


@pytest_asyncio.fixture
async def valid_add_request() -> dict[str, Any]:
    return {
        "quantity": 5,
        "is_positive": True,
    }


@pytest_asyncio.fixture
async def valid_subtract_request() -> dict[str, Any]:
    return {
        "quantity": 3,
        "is_positive": False,
    }


@pytest_asyncio.fixture
def mock_updated_bondholder() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        quantity=15,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="ROR0000",
        nominal_value=1000.00,
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )


async def test_add_to_bond_purchase_success(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
    mock_current_user: UUID,
) -> None:
    last_update = mock_updated_bondholder.last_update

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(mock_updated_bondholder.id)
    assert data["quantity"] == 15
    assert data["last_update"].replace("Z", "+00:00") == last_update.isoformat()

    mock_use_case.execute.assert_called_once()
    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]

    assert dto.id == valid_purchase_id
    assert dto.user_id == mock_current_user
    assert dto.quantity == 5
    assert dto.is_positive is True


async def test_subtract_from_bond_purchase_success(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_subtract_request: dict,
) -> None:
    mock_response = AsyncMock(
        id=uuid4(),
        quantity=7,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="А",
        nominal_value=100.00,
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(
        f"/bonds/{valid_purchase_id}/add", json=valid_subtract_request
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["quantity"] == 7

    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]

    assert dto.quantity == 3
    assert dto.is_positive is False


async def test_add_to_bond_purchase_missing_quantity(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    invalid_request = {"is_positive": True}

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=invalid_request)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_add_to_bond_purchase_missing_is_positive(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    invalid_request = {"quantity": 5}

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=invalid_request)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_add_to_bond_purchase_invalid_uuid(
    client: TestClient,
    valid_add_request: dict,
) -> None:
    invalid_id = "not-a-valid-uuid"

    response = client.patch(f"/bonds/{invalid_id}/add", json=valid_add_request)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_add_to_bond_purchase_unauthorized(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_to_bond_purchase_not_found(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = NotFoundError("BondHolder not found")

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_to_bond_purchase_user_id_from_authentication(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
    mock_current_user: UUID,
) -> None:
    expected_user_id = mock_current_user

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)
    assert response.status_code == status.HTTP_200_OK

    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]
    assert dto.user_id == expected_user_id


async def test_add_to_bond_purchase_response_structure(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)

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


async def test_add_to_bond_purchase_large_quantity(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    large_quantity_request = {
        "quantity": 10000,
        "is_positive": True,
    }

    mock_response = AsyncMock(
        id=uuid4(),
        quantity=10100,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="ROR0000",
        nominal_value=100.00,
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(
        f"/bonds/{valid_purchase_id}/add", json=large_quantity_request
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["quantity"] == 10100


async def test_add_to_bond_purchase_updates_last_update(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
) -> None:
    original_date = date.today() - timedelta(days=15)
    updated_date = datetime.now(timezone.utc)

    mock_response = AsyncMock(
        id=uuid4(),
        quantity=20,
        purchase_date=original_date,
        last_update=updated_date,
        bond_id=uuid4(),
        series="ROR0000",
        nominal_value=1000.00,
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_add_to_bh_use_case,
    )

    app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=valid_add_request)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    delta = timedelta(seconds=0.05)

    purchase_date_tested = date.fromisoformat(data["purchase_date"])
    purchase_date_expected = date.today() - timedelta(days=15)

    last_update_tested = datetime.fromisoformat(data["last_update"])
    last_update_expected = datetime.now(timezone.utc)

    assert abs(purchase_date_tested - purchase_date_expected) <= delta
    assert abs(last_update_tested - last_update_expected) <= delta
    assert last_update_tested.date() != purchase_date_tested


async def test_add_to_bond_purchase_invalid_json(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    response = client.patch(
        f"/bonds/{valid_purchase_id}/add",
        content="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_add_to_bond_purchase_wrong_data_types(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    invalid_request = {
        "quantity": "five",
        "is_positive": "yes",
    }

    response = client.patch(f"/bonds/{valid_purchase_id}/add", json=invalid_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_add_to_bond_purchase_multiple_operations(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    operations = [
        ({"quantity": 5, "is_positive": True}, 15),
        ({"quantity": 3, "is_positive": False}, 12),
        ({"quantity": 8, "is_positive": True}, 20),
    ]

    for request_data, expected_quantity in operations:
        mock_response = AsyncMock(
            id=uuid4(),
            quantity=expected_quantity,
            purchase_date=date.today(),
            last_update=datetime.now(timezone.utc),
            bond_id=uuid4(),
            series="ROR0000",
            nominal_value=1001.00,
            maturity_period=15,
            initial_interest_rate=5.3,
            first_interest_period=6,
            reference_rate_margin=1.0,
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_response

        from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
            bond_add_to_bh_use_case,
        )

        app.dependency_overrides[bond_add_to_bh_use_case] = lambda: mock_use_case

        response = client.patch(f"/bonds/{valid_purchase_id}/add", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["quantity"] == expected_quantity

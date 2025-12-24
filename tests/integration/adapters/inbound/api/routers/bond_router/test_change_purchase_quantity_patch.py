from typing import Any

from datetime import date, datetime, timezone, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.adapters.inbound.api.main import app


@pytest.fixture
def valid_purchase_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_add_request() -> dict[str, Any]:
    return {
        "new_quantity": 5,
    }


@pytest.fixture
def mock_updated_bondholder() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        quantity=5,
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


def test_change_purchase_quantity_success(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
    mock_current_user: UUID,
) -> None:
    last_update = mock_updated_bondholder.last_update

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        update_bh_quantity_use_case,
    )

    app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(mock_updated_bondholder.id)
    assert data["quantity"] == 5
    assert data["last_update"].replace("Z", "+00:00") == last_update.isoformat()

    mock_use_case.execute.assert_called_once()
    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]

    assert dto.id == valid_purchase_id
    assert dto.user_id == mock_current_user
    assert dto.new_quantity == 5


def test_change_purchase_quantity_invalid_uuid(
    client: TestClient,
    valid_add_request: dict,
) -> None:
    invalid_id = "not-a-valid-uuid"

    response = client.patch(f"api/bonds/{invalid_id}/quantity", json=valid_add_request)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_change_purchase_quantity_unauthorized(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_purchase_quantity_not_found(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = NotFoundError("BondHolder not found")

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        update_bh_quantity_use_case,
    )

    app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_change_purchase_quantity_user_id_from_authentication(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
    mock_current_user: UUID,
) -> None:
    expected_user_id = mock_current_user

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        update_bh_quantity_use_case,
    )

    app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
    )
    assert response.status_code == status.HTTP_200_OK

    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]
    assert dto.user_id == expected_user_id


def test_change_purchase_quantity_response_structure(
    client: TestClient,
    valid_purchase_id: UUID,
    valid_add_request: dict,
    mock_updated_bondholder: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bondholder

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        update_bh_quantity_use_case,
    )

    app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
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


def test_change_purchase_quantity_updates_last_update(
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

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        update_bh_quantity_use_case,
    )

    app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=valid_add_request
    )

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


def test_change_purchase_quantity_invalid_json(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity",
        content="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_change_purchase_quantity_wrong_data_types(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    invalid_request = {
        "quantity": "five",
    }

    response = client.patch(
        f"api/bonds/{valid_purchase_id}/quantity", json=invalid_request
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_change_purchase_quantity_multiple_operations(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    operations = [
        ({"new_quantity": 5}, 5),
        ({"new_quantity": 3}, 3),
        ({"new_quantity": 8}, 8),
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

        from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
            update_bh_quantity_use_case,
        )

        app.dependency_overrides[update_bh_quantity_use_case] = lambda: mock_use_case

        response = client.patch(
            f"api/bonds/{valid_purchase_id}/quantity", json=request_data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["quantity"] == expected_quantity

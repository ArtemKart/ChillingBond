from decimal import Decimal
from typing import Any

from datetime import date
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from starlette.testclient import TestClient

from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.inbound.api.main import app


@pytest.fixture
def valid_bond_data() -> dict[str, Any]:
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
def mock_use_case_response() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        user_id=uuid4(),
        quantity=10,
        purchase_date=date.today(),
        last_update=date.today(),
        bond_id=uuid4(),
        series="ROR1206",
        nominal_value=Decimal("100.0"),
        maturity_period=12,
        initial_interest_rate=Decimal("4.75"),
        first_interest_period=1,
        reference_rate_margin=Decimal("0.0"),
    )


def test_create_bond_purchase_success(
    client: TestClient,
    valid_bond_data: dict[str, Any],
    mock_use_case_response: AsyncMock,
) -> None:
    purchase_date = valid_bond_data["purchase_date"]
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_use_case_response

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        create_bondholder_use_case,
    )

    app.dependency_overrides[create_bondholder_use_case] = lambda: mock_use_case

    response = client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["id"] == str(mock_use_case_response.id)
    assert data["quantity"] == 10
    assert data["purchase_date"] == purchase_date
    assert data["bond_id"] == str(mock_use_case_response.bond_id)
    assert data["series"] == "ROR1206"
    assert Decimal(data["nominal_value"]) == Decimal("100.00")
    assert data["maturity_period"] == 12
    assert Decimal(data["initial_interest_rate"]) == Decimal("4.75")
    assert data["first_interest_period"] == 1
    assert Decimal(data["reference_rate_margin"]) == Decimal("0.00")

    mock_use_case.execute.assert_called_once()
    call_args = mock_use_case.execute.call_args
    bondholder_dto, bond_dto = call_args[0]

    assert bondholder_dto.quantity == 10
    assert isinstance(bondholder_dto.purchase_date, date)
    assert bondholder_dto.purchase_date.isoformat() == purchase_date
    assert bond_dto.series == "ROR1206"
    assert Decimal(bond_dto.nominal_value) == Decimal("100.00")


def test_create_bond_purchase_missing_required_fields(client: TestClient) -> None:
    incomplete_data = {
        "quantity": 10,
        "series": "ROR1206",
        # Missing other required fields
    }
    response = client.post("/bonds", json=incomplete_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_bond_purchase_invalid_quantity(
    client: TestClient, valid_bond_data: dict[str, Any]
) -> None:

    valid_bond_data["quantity"] = -5
    response = client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_bond_purchase_invalid_date_format(
    client: TestClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["purchase_date"] = "invalid-date"
    response = client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_bond_purchase_invalid_nominal_value(
    client: TestClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["nominal_value"] = "-1000"
    response = client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_bond_purchase_invalid_maturity_period(
    client: TestClient, valid_bond_data: dict[str, Any]
) -> None:
    valid_bond_data["maturity_period"] = 0
    response = client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_bond_purchase_unauthorized(
    valid_bond_data: dict[str, Any],
) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)

    test_client = TestClient(app)

    response = test_client.post("/bonds", json=valid_bond_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_bond_purchase_use_case_exception(
    client: TestClient, valid_bond_data: dict[str, Any]
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = SQLAlchemyRepositoryError(
        "Failed to save BondHolder object"
    )

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        create_bondholder_use_case,
    )

    app.dependency_overrides[create_bondholder_use_case] = lambda: mock_use_case

    response = client.post("/bonds", json=valid_bond_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_bond_purchase_with_decimal_values(
    client: TestClient,
    valid_bond_data: dict[str, Any],
    mock_use_case_response: AsyncMock,
) -> None:
    valid_bond_data["nominal_value"] = "1000.0"
    valid_bond_data["initial_interest_rate"] = "4.25"
    valid_bond_data["reference_rate_margin"] = "2.15"

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_use_case_response

    from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
        create_bondholder_use_case,
    )

    app.dependency_overrides[create_bondholder_use_case] = lambda: mock_use_case

    response = client.post("/bonds", json=valid_bond_data)

    assert response.status_code == status.HTTP_201_CREATED
    call_args = mock_use_case.execute.call_args[0]
    bond_dto = call_args[1]
    assert isinstance(bond_dto.nominal_value, Decimal)
    assert isinstance(bond_dto.initial_interest_rate, Decimal)
    assert isinstance(bond_dto.reference_rate_margin, Decimal)

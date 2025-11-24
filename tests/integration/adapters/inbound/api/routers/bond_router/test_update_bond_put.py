from decimal import Decimal
from typing import Any
from uuid import uuid4, UUID
from unittest.mock import AsyncMock

import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient

from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
def valid_bond_id() -> UUID:
    return uuid4()


@pytest_asyncio.fixture
def valid_update_request() -> dict[str, Any]:
    return {
        "nominal_value": 100.00,
        "series": "ROR1000",
        "maturity_period": 18,
        "initial_interest_rate": 6.5,
        "first_interest_period": 4,
        "reference_rate_margin": 1.5,
    }


@pytest_asyncio.fixture
def partial_update_request() -> dict[str, float]:
    return {
        "nominal_value": 2000.00,
        "initial_interest_rate": 7.0,
    }


@pytest_asyncio.fixture
def mock_updated_bond() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        nominal_value=1500.00,
        series="ROR0000",
        maturity_period=18,
        initial_interest_rate=6.5,
        first_interest_period=4,
        reference_rate_margin=1.5,
    )


async def test_update_bond_success_full_update(
    client: TestClient,
    valid_bond_id: UUID,
    valid_update_request: dict,
    mock_updated_bond: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bond

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(
        f"/bonds/{valid_bond_id}/specification", json=valid_update_request
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["nominal_value"] == 1500.00
    assert data["series"] == "ROR0000"
    assert data["maturity_period"] == 18
    assert data["initial_interest_rate"] == 6.5
    assert data["first_interest_period"] == 4
    assert data["reference_rate_margin"] == 1.5

    mock_use_case.execute.assert_called_once()
    call_args = mock_use_case.execute.call_args

    assert call_args.kwargs["bond_id"] == valid_bond_id
    dto = call_args.kwargs["dto"]
    assert dto.nominal_value == 100.00
    assert dto.series == "ROR1000"
    assert dto.maturity_period == 18


async def test_update_bond_success_partial_update(
    client: TestClient,
    valid_bond_id: UUID,
    partial_update_request: dict,
) -> None:
    mock_response = AsyncMock(
        id=uuid4(),
        nominal_value=2000.00,
        series="ROR0000",
        maturity_period=12,
        initial_interest_rate=7.0,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(
        f"/bonds/{valid_bond_id}/specification", json=partial_update_request
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["nominal_value"] == 2000.00
    assert data["initial_interest_rate"] == 7.0

    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]
    assert dto.nominal_value == 2000.00
    assert dto.initial_interest_rate == 7.0


async def test_update_bond_not_found(
    client: TestClient,
    valid_bond_id: UUID,
    valid_update_request: dict,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = NotFoundError("Bond not found")

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(
        f"/bonds/{valid_bond_id}/specification", json=valid_update_request
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_bond_invalid_uuid(
    client: TestClient,
    valid_update_request: dict,
) -> None:
    invalid_id = "not-a-valid-uuid"

    response = client.put(
        f"/bonds/{invalid_id}/specification", json=valid_update_request
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_unauthorized() -> None:
    bond_id = uuid4()
    update_request = {
        "nominal_value": 1500.00,
        "series": "ROR9999",
    }

    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)
    test_client = TestClient(app)

    response = test_client.put(f"/bonds/{bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_bond_missing_required_fields(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    empty_request: dict = {}

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=empty_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_invalid_nominal_value(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    invalid_request = {
        "nominal_value": -1000.00,
        "series": "ROR5555",
    }

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=invalid_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_invalid_maturity_period(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    invalid_request = {
        "nominal_value": 1000.00,
        "maturity_period": -12,
    }

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=invalid_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_invalid_interest_rate(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    invalid_request = {
        "nominal_value": 1000.00,
        "initial_interest_rate": -5.5,
    }

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=invalid_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_response_structure(
    client: TestClient,
    valid_bond_id: UUID,
    valid_update_request: dict,
    mock_updated_bond: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bond

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(
        f"/bonds/{valid_bond_id}/specification", json=valid_update_request
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

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


async def test_update_bond_decimal_precision(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    update_request = {
        "nominal_value": 1234.56,
        "initial_interest_rate": 7.25,
        "reference_rate_margin": 2.15,
    }

    mock_response = AsyncMock(
        id=uuid4(),
        nominal_value=1234.56,
        series="ROR0000",
        maturity_period=12,
        initial_interest_rate=7.25,
        first_interest_period=3,
        reference_rate_margin=2.15,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["nominal_value"] == 1234.56
    assert data["initial_interest_rate"] == 7.25
    assert data["reference_rate_margin"] == 2.15

    call_args = mock_use_case.execute.call_args
    dto = call_args.kwargs["dto"]
    assert isinstance(dto.nominal_value, float)
    assert isinstance(dto.initial_interest_rate, float)


async def test_update_bond_different_series(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    series_list = ["ROR0000", "ROR1111", "ROR2222", "ROR3333"]

    for series in series_list:
        update_request = {
            "series": series,
            "nominal_value": 1000.00,
        }

        mock_response = AsyncMock(
            id=uuid4(),
            nominal_value=1000.00,
            series=series,
            maturity_period=12,
            initial_interest_rate=5.5,
            first_interest_period=3,
            reference_rate_margin=1.2,
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_response

        from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
            bond_update_use_case,
        )

        app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

        response = client.put(
            f"/bonds/{valid_bond_id}/specification", json=update_request
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["series"] == series


async def test_update_bond_invalid_json(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    response = client.put(
        f"/bonds/{valid_bond_id}/specification",
        data="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_wrong_data_types(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    invalid_request = {
        "nominal_value": "one thousand",
        "maturity_period": "twelve months",
        "initial_interest_rate": "five percent",
    }

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=invalid_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_only_nominal_value(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    update_request = {
        "nominal_value": 3000.00,
    }

    mock_response = AsyncMock(
        id=uuid4(),
        nominal_value=3000.00,
        series="ROR0000",
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nominal_value"] == 3000.00


async def test_update_bond_only_series(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    update_request = {
        "series": "ROR0000",
    }

    mock_response = AsyncMock(
        id=uuid4(),
        nominal_value=1000.00,
        series="ROR9999",
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=3,
        reference_rate_margin=1.2,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_response

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["series"] == "ROR9999"


async def test_update_bond_multiple_updates_same_bond(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    updates = [
        ({"nominal_value": 1000.00}, 1000.00),
        ({"nominal_value": 1500.00}, 1500.00),
        ({"nominal_value": 2000.00}, 2000.00),
    ]

    for update_request, expected_value in updates:
        mock_response = AsyncMock(
            id=uuid4(),
            nominal_value=expected_value,
            series="ROR0000",
            maturity_period=12,
            initial_interest_rate=5.5,
            first_interest_period=3,
            reference_rate_margin=1.2,
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_response

        from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
            bond_update_use_case,
        )

        app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

        response = client.put(
            f"/bonds/{valid_bond_id}/specification", json=update_request
        )

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(str(response.json()["nominal_value"])) == expected_value


async def test_update_bond_with_all_fields_as_none(
    client: TestClient,
    valid_bond_id: UUID,
) -> None:
    update_request = {
        "nominal_value": None,
        "series": None,
        "maturity_period": None,
        "initial_interest_rate": None,
        "first_interest_period": None,
        "reference_rate_margin": None,
    }

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_bond_extra_fields_ignored(
    client: TestClient,
    valid_bond_id: UUID,
    mock_updated_bond: AsyncMock,
) -> None:
    update_request = {
        "nominal_value": 1500.00,
        "series": "ROR1111",
        "extra_field": "should be ignored",
        "another_extra": 123,
    }

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_updated_bond

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(f"/bonds/{valid_bond_id}/specification", json=update_request)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "extra_field" not in data
    assert "another_extra" not in data


async def test_update_bond_use_case_exception(
    client: TestClient,
    valid_bond_id: UUID,
    valid_update_request: dict,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = SQLAlchemyRepositoryError(
        "Failed to update bond"
    )

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bond_update_use_case,
    )

    app.dependency_overrides[bond_update_use_case] = lambda: mock_use_case

    response = client.put(
        f"/bonds/{valid_bond_id}/specification", json=valid_update_request
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4, UUID
from unittest.mock import AsyncMock

import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient

from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
def valid_purchase_id() -> UUID:
    return uuid4()


@pytest_asyncio.fixture
def mock_bond_dto() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        quantity=10,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="ROR0000",
        nominal_value=100.00,
        maturity_period=12,
        initial_interest_rate=5.5,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )


async def test_get_bond_success(
    client: TestClient,
    valid_purchase_id: UUID,
    mock_bond_dto: AsyncMock,
    mock_current_user: UUID,
) -> None:
    purchase_date = mock_bond_dto.purchase_date
    last_update = mock_bond_dto.last_update

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_bond_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(mock_bond_dto.id)
    assert data["quantity"] == 10
    assert data["purchase_date"] == purchase_date.isoformat()
    assert data["last_update"].replace("Z", "+00:00") == last_update.isoformat()
    assert data["bond_id"] == str(mock_bond_dto.bond_id)
    assert data["series"] == "ROR0000"
    assert data["nominal_value"] == 100.00
    assert data["maturity_period"] == 12
    assert data["initial_interest_rate"] == 5.5
    assert data["first_interest_period"] == 1
    assert data["reference_rate_margin"] == 0.0

    mock_use_case.execute.assert_called_once_with(
        bondholder_id=valid_purchase_id, user_id=mock_current_user
    )


async def test_get_bond_not_found(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = NotFoundError("BondHolder not found")

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "BondHolder not found"


async def test_get_bond_invalid_token(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    from src.domain.exceptions import InvalidTokenError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = InvalidTokenError("Invalid credentials")

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


async def test_get_bond_unauthorized() -> None:
    purchase_id = uuid4()

    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)
    test_client = TestClient(app)

    response = test_client.get(f"/bonds/{purchase_id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_bond_invalid_uuid_format(
    client: TestClient,
) -> None:
    invalid_id = "not-a-valid-uuid"
    response = client.get(f"/bonds/{invalid_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_get_bond_different_user_cannot_access(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = NotFoundError("BondHolder not found")

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_bond_response_structure(
    client: TestClient,
    valid_purchase_id: UUID,
    mock_bond_dto: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_bond_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

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


async def test_get_bond_decimal_precision(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    mock_dto = AsyncMock(
        id=uuid4(),
        quantity=7,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="ROR0000",
        nominal_value=1234.56,
        maturity_period=15,
        initial_interest_rate=7.25,
        first_interest_period=3,
        reference_rate_margin=2.15,
    )
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["nominal_value"] == 1234.56
    assert data["initial_interest_rate"] == 7.25
    assert data["reference_rate_margin"] == 2.15


async def test_get_bond_date_serialization(
    client: TestClient,
    valid_purchase_id: UUID,
    mock_bond_dto: AsyncMock,
) -> None:
    purchase_date = mock_bond_dto.purchase_date
    last_update = mock_bond_dto.last_update

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_bond_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["purchase_date"] == purchase_date.isoformat()
    assert data["last_update"].replace("Z", "+00:00") == last_update.isoformat()


async def test_get_bond_user_id_from_authentication(
    client: TestClient,
    valid_purchase_id: UUID,
    mock_bond_dto: AsyncMock,
    mock_current_user: UUID,
) -> None:
    expected_user_id = mock_current_user

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_bond_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response = client.get(f"/bonds/{valid_purchase_id}")

    assert response.status_code == status.HTTP_200_OK
    mock_use_case.execute.assert_called_once_with(
        bondholder_id=valid_purchase_id, user_id=expected_user_id
    )


async def test_get_bond_with_different_series(
    client: TestClient,
    valid_purchase_id: UUID,
) -> None:
    series_list = ["ROR0000", "ROR1111", "ROR2222", "ROR3333"]

    for series in series_list:
        mock_dto = AsyncMock(
            id=uuid4(),
            quantity=5,
            purchase_date=date.today(),
            last_update=datetime.now(timezone.utc),
            bond_id=uuid4(),
            series=series,
            nominal_value=Decimal("1500.00"),
            maturity_period=18,
            initial_interest_rate=Decimal("6.0"),
            first_interest_period=4,
            reference_rate_margin=Decimal("1.5"),
        )

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_dto

        from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
            bh_get_use_case,
        )

        app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

        response = client.get(f"/bonds/{valid_purchase_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["series"] == series


async def test_get_bond_multiple_calls_different_ids(
    client: TestClient,
    mock_bond_dto: AsyncMock,
) -> None:
    purchase_id_1 = uuid4()
    purchase_id_2 = uuid4()

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_bond_dto

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_use_case,
    )

    app.dependency_overrides[bh_get_use_case] = lambda: mock_use_case

    response_1 = client.get(f"/bonds/{purchase_id_1}")
    response_2 = client.get(f"/bonds/{purchase_id_2}")

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK

    assert mock_use_case.execute.call_count == 2
    first_call = mock_use_case.execute.call_args_list[0]
    second_call = mock_use_case.execute.call_args_list[1]

    assert first_call.kwargs["bondholder_id"] == purchase_id_1
    assert second_call.kwargs["bondholder_id"] == purchase_id_2

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4, UUID

import pytest_asyncio
from starlette import status
from starlette.testclient import TestClient

from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
def mock_bondholder_response() -> AsyncMock:
    return AsyncMock(
        id=uuid4(),
        quantity=10,
        purchase_date=date.today(),
        last_update=datetime.now(timezone.utc),
        bond_id=uuid4(),
        series="ROR1206",
        nominal_value=100.0,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )


@pytest_asyncio.fixture
def mock_multiple_bondholders() -> list[AsyncMock]:
    return [
        AsyncMock(
            id=uuid4(),
            quantity=10,
            purchase_date=date.today(),
            last_update=datetime.now(timezone.utc),
            bond_id=uuid4(),
            series="ROR1206",
            nominal_value=100.0,
            maturity_period=12,
            initial_interest_rate=4.75,
            first_interest_period=1,
            reference_rate_margin=0.0,
        ),
        AsyncMock(
            id=uuid4(),
            quantity=5,
            purchase_date=date.today(),
            last_update=datetime.now(timezone.utc),
            bond_id=uuid4(),
            series="ROR0000",
            nominal_value=101.0,
            maturity_period=12,
            initial_interest_rate=5,
            first_interest_period=1,
            reference_rate_margin=0.1,
        ),
        AsyncMock(
            id=uuid4(),
            quantity=15,
            purchase_date=date.today(),
            last_update=datetime.now(timezone.utc),
            bond_id=uuid4(),
            series="ROR1111",
            nominal_value=102.0,
            maturity_period=12,
            initial_interest_rate=3,
            first_interest_period=1,
            reference_rate_margin=0.3,
        ),
    ]


async def test_get_all_bonds_success_with_multiple_bonds(
    client: TestClient,
    mock_multiple_bondholders: list[AsyncMock],
    mock_current_user: UUID,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = mock_multiple_bondholders

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    assert data[0]["id"] == str(mock_multiple_bondholders[0].id)
    assert data[0]["quantity"] == 10
    assert data[0]["series"] == "ROR1206"
    assert data[0]["nominal_value"] == 100.00

    assert data[1]["quantity"] == 5
    assert data[1]["series"] == "ROR0000"
    assert data[1]["nominal_value"] == 101.00

    mock_use_case.execute.assert_called_once_with(user_id=mock_current_user)


async def test_get_all_bonds_success_with_single_bond(
    client: TestClient,
    mock_bondholder_response: AsyncMock,
    mock_current_user: UUID,
) -> None:
    purchase_date = mock_bondholder_response.purchase_date
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_bondholder_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(mock_bondholder_response.id)
    assert data[0]["quantity"] == 10
    assert data[0]["purchase_date"] == purchase_date.isoformat()
    assert data[0]["bond_id"] == str(mock_bondholder_response.bond_id)


async def test_get_all_bonds_empty_list(
    client: TestClient,
    mock_current_user: UUID,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = []

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0
    mock_use_case.execute.assert_called_once_with(user_id=mock_current_user)


async def test_get_all_bonds_unauthorized() -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides.pop(current_user, None)
    test_client = TestClient(app)

    response = test_client.get("/bonds")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# async def test_get_all_bonds_use_case_exception(
#     client: TestClient,
#     mock_current_user: UUID,
# ) -> None:
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.side_effect = Exception("Database connection error")
#
#     from src.adapters.inbound.api.dependencies.bond_use_cases_deps import bh_get_all_use_case
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     response = client.get("/bonds")
#
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


async def test_get_all_bonds_user_id_from_authentication(
    client: TestClient,
    mock_bondholder_response: AsyncMock,
    mock_current_user: UUID,
) -> None:
    expected_user_id = mock_current_user
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_bondholder_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    mock_use_case.execute.assert_called_once_with(user_id=expected_user_id)


async def test_get_all_bonds_response_structure(
    client: TestClient,
    mock_bondholder_response: AsyncMock,
) -> None:
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_bondholder_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

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
        assert field in data[0]


async def test_get_all_bonds_decimal_precision(
    client: TestClient,
    mock_current_user: UUID,
) -> None:
    mock_response = AsyncMock(
        id=uuid4(),
        quantity=7,
        purchase_date=date.today(),
        last_update=date.today(),
        bond_id=uuid4(),
        series="ROR2222",
        nominal_value=1234.56,
        maturity_period=15,
        initial_interest_rate=7.25,
        first_interest_period=5,
        reference_rate_margin=2.15,
    )

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data[0]["nominal_value"] == 1234.56
    assert data[0]["initial_interest_rate"] == 7.25
    assert data[0]["reference_rate_margin"] == 2.15


async def test_get_all_bonds_date_serialization(
    client: TestClient,
    mock_bondholder_response: AsyncMock,
) -> None:
    purchase_date = mock_bondholder_response.purchase_date
    last_update = mock_bondholder_response.last_update
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_bondholder_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    response = client.get("/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data[0]["purchase_date"] == purchase_date.isoformat()
    assert data[0]["last_update"].replace("Z", "+00:00") == last_update.isoformat()


async def test_get_all_bonds_different_users_isolation(
    mock_bondholder_response: AsyncMock,
) -> None:
    user_id_1 = uuid4()
    user_id_2 = uuid4()

    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = [mock_bondholder_response]

    from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
        bh_get_all_use_case,
    )
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case

    app.dependency_overrides[current_user] = lambda: user_id_1
    client_1 = TestClient(app)
    response_1 = client_1.get("/bonds")
    assert response_1.status_code == status.HTTP_200_OK

    first_call = mock_use_case.execute.call_args_list[0]
    assert first_call.kwargs["user_id"] == user_id_1

    app.dependency_overrides[current_user] = lambda: user_id_2
    client_2 = TestClient(app)
    response_2 = client_2.get("/bonds")
    assert response_2.status_code == status.HTTP_200_OK

    second_call = mock_use_case.execute.call_args_list[1]
    assert second_call.kwargs["user_id"] == user_id_2
    assert first_call.kwargs["user_id"] != second_call.kwargs["user_id"]

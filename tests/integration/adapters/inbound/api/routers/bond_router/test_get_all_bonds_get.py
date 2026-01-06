from datetime import date
from uuid import uuid4, UUID

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import BondHolder as BondholderModel


@pytest_asyncio.fixture
async def multiple_bondholders(
    t_session: AsyncSession, t_current_user: UUID, t_bond: BondModel
) -> list[BondholderModel]:
    n = 3
    bhs = [
        BondholderModel(
            id=uuid4(),
            user_id=t_current_user,
            bond_id=t_bond.id,
            quantity=10 * (i + 1),
            purchase_date=date.today(),
            last_update=None,
        )
        for i in range(n)
    ]
    t_session.add_all(bhs)
    await t_session.commit()
    [await t_session.refresh(bhs[i]) for i in range(n)]
    return bhs


async def test_success_with_multiple_bonds(
    client: AsyncClient,
    multiple_bondholders: list[BondholderModel],
    t_bond: BondModel,
) -> None:

    response = await client.get("api/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    for i, bh in enumerate(multiple_bondholders):
        assert data[i]["id"] == str(bh.id)
        assert data[i]["bond_id"] == str(bh.bond_id)
        assert data[i]["quantity"] == bh.quantity
        assert data[0]["series"] == t_bond.series
        assert data[0]["purchase_date"] == bh.purchase_date.isoformat()
        assert data[0]["nominal_value"] == t_bond.nominal_value
        assert data[0]["maturity_period"] == t_bond.maturity_period
        assert data[0]["initial_interest_rate"] == t_bond.initial_interest_rate
        assert data[0]["reference_rate_margin"] == t_bond.reference_rate_margin
        assert data[0]["first_interest_period"] == t_bond.first_interest_period


async def test_success_with_single_bond(
    client: AsyncClient,
    t_bondholder: BondholderModel,
) -> None:

    response = await client.get("api/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(t_bondholder.id)
    assert data[0]["quantity"] == 10
    assert data[0]["purchase_date"] == t_bondholder.purchase_date.isoformat()
    assert data[0]["bond_id"] == str(t_bondholder.bond_id)


async def test_empty_list(
    client: AsyncClient,
    t_session: AsyncSession,
    t_current_user: UUID,
) -> None:

    bhs = await t_session.execute(
        "SELECT * FROM bondholder WHERE user_id = :t_current_user",
        {"t_current_user": str(t_current_user)},
    )
    bhs = bhs.scalars().all()
    assert not bhs

    response = await client.get("api/bonds")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0


# def test_get_all_bonds_unauthorized() -> None:
#     from src.adapters.inbound.api.dependencies.current_user_deps import current_user
#
#     app.dependency_overrides.pop(current_user, None)
#     test_client = AsyncClient(app)
#
#     response = test_client.get("api/bonds")
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# def test_get_all_bonds_user_id_from_authentication(
#     client: AsyncClient,
#     mock_bondholder_response: AsyncMock,
#     mock_current_user: UUID,
# ) -> None:
#     expected_user_id = mock_current_user
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.return_value = [mock_bondholder_response]
#
#     from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
#         bh_get_all_use_case,
#     )
#
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     response = client.get("api/bonds")
#
#     assert response.status_code == status.HTTP_200_OK
#     mock_use_case.execute.assert_called_once_with(user_id=expected_user_id)
#
#
# def test_get_all_bonds_response_structure(
#     client: AsyncClient,
#     mock_bondholder_response: AsyncMock,
# ) -> None:
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.return_value = [mock_bondholder_response]
#
#     from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
#         bh_get_all_use_case,
#     )
#
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     response = client.get("api/bonds")
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#
#     required_fields = [
#         "id",
#         "quantity",
#         "purchase_date",
#         "last_update",
#         "bond_id",
#         "series",
#         "nominal_value",
#         "maturity_period",
#         "initial_interest_rate",
#         "first_interest_period",
#         "reference_rate_margin",
#     ]
#
#     for field in required_fields:
#         assert field in data[0]
#
#
# def test_get_all_bonds_decimal_precision(
#     client: AsyncClient,
# ) -> None:
#     mock_response = AsyncMock(
#         id=uuid4(),
#         quantity=7,
#         purchase_date=date.today(),
#         last_update=date.today(),
#         bond_id=uuid4(),
#         series="ROR2222",
#         nominal_value=Decimal("1234.56"),
#         maturity_period=15,
#         initial_interest_rate=Decimal("7.25"),
#         first_interest_period=5,
#         reference_rate_margin=Decimal("2.15"),
#     )
#
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.return_value = [mock_response]
#
#     from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
#         bh_get_all_use_case,
#     )
#
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     response = client.get("api/bonds")
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#
#     assert Decimal(data[0]["nominal_value"]).quantize(Decimal("0.01")) == Decimal(
#         "1234.56"
#     )
#     assert Decimal(data[0]["initial_interest_rate"]).quantize(
#         Decimal("0.01")
#     ) == Decimal("7.25")
#     assert Decimal(data[0]["reference_rate_margin"]).quantize(
#         Decimal("0.01")
#     ) == Decimal("2.15")
#
#
# def test_get_all_bonds_date_serialization(
#     client: AsyncClient,
#     mock_bondholder_response: AsyncMock,
# ) -> None:
#     purchase_date = mock_bondholder_response.purchase_date
#     last_update = mock_bondholder_response.last_update
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.return_value = [mock_bondholder_response]
#
#     from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
#         bh_get_all_use_case,
#     )
#
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     response = client.get("api/bonds")
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#
#     assert data[0]["purchase_date"] == purchase_date.isoformat()
#     assert data[0]["last_update"].replace("Z", "+00:00") == last_update.isoformat()
#
#
# def test_get_all_bonds_different_users_isolation(
#     mock_bondholder_response: AsyncMock,
# ) -> None:
#     user_id_1 = uuid4()
#     user_id_2 = uuid4()
#
#     mock_use_case = AsyncMock()
#     mock_use_case.execute.return_value = [mock_bondholder_response]
#
#     from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
#         bh_get_all_use_case,
#     )
#     from src.adapters.inbound.api.dependencies.current_user_deps import current_user
#
#     app.dependency_overrides[bh_get_all_use_case] = lambda: mock_use_case
#
#     app.dependency_overrides[current_user] = lambda: user_id_1
#     client_1 = AsyncClient(app)
#     response_1 = client_1.get("api/bonds")
#     assert response_1.status_code == status.HTTP_200_OK
#
#     first_call = mock_use_case.execute.call_args_list[0]
#     assert first_call.kwargs["user_id"] == user_id_1
#
#     app.dependency_overrides[current_user] = lambda: user_id_2
#     client_2 = AsyncClient(app)
#     response_2 = client_2.get("api/bonds")
#     assert response_2.status_code == status.HTTP_200_OK
#
#     second_call = mock_use_case.execute.call_args_list[1]
#     assert second_call.kwargs["user_id"] == user_id_2
#     assert first_call.kwargs["user_id"] != second_call.kwargs["user_id"]

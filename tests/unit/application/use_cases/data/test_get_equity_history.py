from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from src.application.dto.data import EquityDTO
from src.application.dto.user import UserDTO
from src.application.use_cases.data.get_equity_history import GetEquityHistoryUseCase


@pytest.fixture
def use_case(
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_analytics_service: Mock,
) -> GetEquityHistoryUseCase:
    return GetEquityHistoryUseCase(
        bh_repo=mock_bondholder_repo,
        bond_repo=mock_bond_repo,
        service=mock_analytics_service,
    )


@pytest.fixture
def user_dto() -> UserDTO:
    return UserDTO(id=uuid4(), email="test@example.com", name=None)


async def test_execute_returns_empty_when_no_bondholders(
    use_case: GetEquityHistoryUseCase,
    mock_bondholder_repo: AsyncMock,
    user_dto: UserDTO,
) -> None:
    mock_bondholder_repo.get_all.return_value = []

    result: EquityDTO = await use_case.execute(user_dto)

    assert isinstance(result, EquityDTO)
    assert result.data == []
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_dto.id)


async def test_execute_calls_repo_with_correct_user_id(
    use_case: GetEquityHistoryUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_analytics_service: Mock,
    user_dto: UserDTO,
) -> None:
    mock_bondholder_repo.get_all.return_value = []

    await use_case.execute(user_dto)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_dto.id)


async def test_execute_passes_bondholder_data_to_service(
    use_case: GetEquityHistoryUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_analytics_service: Mock,
    user_dto: UserDTO,
) -> None:
    class MockBondHolder:
        def __init__(self, bond_id: UUID, id: UUID) -> None:
            self.bond_id = bond_id
            self.id = id

    class MockBond:
        def __init__(self, id: UUID, nominal_value: Decimal) -> None:
            self.id = id
            self.nominal_value = nominal_value

    bond_id = uuid4()
    nominal_value = Decimal("1000")

    bh1 = MockBondHolder(bond_id, uuid4())
    bh2 = MockBondHolder(bond_id, uuid4())

    mock_bondholder_repo.get_all.return_value = [bh1, bh2]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {bond_id: MockBond(bond_id, nominal_value)}
    mock_analytics_service.get_equity_history.return_value = []

    await use_case.execute(user_dto)

    call_args = mock_analytics_service.get_equity_history.call_args[1]
    bondholder_data = call_args["bondholder_data"]

    assert len(bondholder_data) == 2
    assert bondholder_data[0][1] == nominal_value
    assert bondholder_data[1][1] == nominal_value


async def test_execute_returns_history_data_from_service(
    use_case: GetEquityHistoryUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_analytics_service: Mock,
    user_dto: UserDTO,
) -> None:
    class MockBondHolder:
        def __init__(self, bond_id: UUID) -> None:
            self.bond_id = bond_id

    class MockBond:
        def __init__(self, id: UUID, nominal_value: Decimal) -> None:
            self.id = id
            self.nominal_value = nominal_value

    bond_id: UUID = uuid4()

    mock_bondholder_repo.get_all.return_value = [MockBondHolder(bond_id)]
    mock_bond_repo.get_many.return_value = [MockBond(bond_id, Decimal("1000"))]

    expected_history: list[tuple[date, Decimal]] = [
        (date(2024, 1, 1), Decimal("1000")),
        (date(2024, 2, 1), Decimal("2000")),
    ]
    mock_analytics_service.get_equity_history.return_value = expected_history

    result = await use_case.execute(user_dto)

    assert result.data == expected_history


async def test_execute_handles_multiple_bondholders_multiple_bonds(
    use_case: GetEquityHistoryUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_analytics_service: Mock,
    user_dto: UserDTO,
) -> None:
    class MockBondHolder:
        def __init__(self, bond_id: UUID, id: UUID) -> None:
            self.bond_id = bond_id
            self.id = id

    class MockBond:
        def __init__(self, id: UUID, nominal_value: Decimal) -> None:
            self.id = id
            self.nominal_value = nominal_value

    bond_id_1: UUID = uuid4()
    bond_id_2: UUID = uuid4()

    mock_bondholder_repo.get_all.return_value = [
        MockBondHolder(bond_id_1, uuid4()),
        MockBondHolder(bond_id_2, uuid4()),
        MockBondHolder(bond_id_1, uuid4()),
    ]

    mock_bond_repo.get_many.return_value = [
        MockBond(bond_id_1, Decimal("1000")),
        MockBond(bond_id_2, Decimal("2000")),
    ]

    expected_history: list[tuple[date, Decimal]] = [
        (date(2024, 1, 1), Decimal("5000")),
    ]
    mock_analytics_service.get_equity_history.return_value = expected_history

    result: EquityDTO = await use_case.execute(user_dto)

    assert result.data == expected_history
    call_args = mock_analytics_service.get_equity_history.call_args[1]
    bondholder_data = call_args["bondholder_data"]
    assert len(bondholder_data) == 3


def test_to_dto_converts_data_to_equity_dto(use_case: GetEquityHistoryUseCase) -> None:
    data: list[tuple[date, Decimal]] = [
        (date(2024, 1, 1), Decimal("100")),
        (date(2024, 2, 1), Decimal("200")),
    ]

    result: EquityDTO = use_case._to_dto(data)

    assert isinstance(result, EquityDTO)
    assert result.data == data


def test_to_dto_handles_empty_data(
    use_case: GetEquityHistoryUseCase,
) -> None:
    data: list[tuple[date, Decimal]] = []

    result: EquityDTO = use_case._to_dto(data)

    assert isinstance(result, EquityDTO)
    assert result.data == []

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.dto.calculations import MonthlyIncomeResponseDTO
from src.application.use_cases.calculations.calculate_income import (
    CalculateIncomeUseCase,
)
from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.exceptions import NotFoundError
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


@pytest.fixture
def use_case(
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> CalculateIncomeUseCase:
    return CalculateIncomeUseCase(
        bh_income_calculator=BondHolderIncomeCalculator(),
        bondholder_repo=mock_bondholder_repo,
        bond_repo=mock_bond_repo,
        reference_rate_repo=mock_reference_rate_repo,
    )


@pytest.fixture
def user_mock() -> Mock:
    user = Mock()
    user.id = uuid4()
    return user


@pytest.fixture
def reference_rate_mock() -> Mock:
    rate = Mock()
    rate.id = uuid4()
    rate.value = Decimal("5.75")
    rate.start_date = date(2024, 1, 1)
    rate.end_date = None
    return rate


@pytest.fixture
def mock_bondholders(bond_entity_mock: Mock) -> list[Mock]:
    bh1 = Mock(spec=BondHolderEntity)
    bh1.id = uuid4()
    bh1.bond_id = bond_entity_mock.id
    bh1.user_id = uuid4()
    bh1.quantity = 100
    bh1.purchase_date = date.today()
    bh1.last_update = datetime.now()

    bh2 = Mock(spec=BondHolderEntity)
    bh2.id = uuid4()
    bh2.bond_id = bond_entity_mock.id
    bh2.user_id = uuid4()
    bh2.quantity = 100
    bh2.purchase_date = date.today()
    bh2.last_update = datetime.now()
    return [bh1, bh2]


async def test_happy_path(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bondholders: list[Mock],
    reference_rate_mock: Mock,
    bond_entity_mock: Mock,
    user_mock: Mock,
) -> None:

    target_date: date = date(2024, 6, 15)
    mock_bondholder_repo.get_all.return_value = mock_bondholders
    expected_income = {
        mock_bondholders[0].id: Decimal("29.16"),
        mock_bondholders[1].id: Decimal("29.16"),
    }

    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        mbh.bond_id: bond_entity_mock for mbh in mock_bondholders
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == expected_income

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_mock.id)
    mock_bond_repo.fetch_dict_from_bondholders.assert_called_once_with(
        bondholders=mock_bondholders
    )
    mock_reference_rate_repo.get_by_date.assert_called_once_with(target_date=target_date)


async def test_bondholders_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = []

    with pytest.raises(NotFoundError, match="Bondholders not found"):
        await use_case.execute(user_mock, target_date)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_mock.id)


async def test_bonds_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_bondholders: list[Mock],
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {}

    with pytest.raises(NotFoundError, match="Bonds not found"):
        await use_case.execute(user_mock, target_date)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_mock.id)
    mock_bond_repo.fetch_dict_from_bondholders.assert_called_once_with(
        bondholders=mock_bondholders
    )


async def test_reference_rate_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bondholders: list[Mock],
    bond_entity_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        mbh.bond_id: bond_entity_mock for mbh in mock_bondholders
    }
    mock_reference_rate_repo.get_by_date.return_value = None

    with pytest.raises(
        NotFoundError, match="Reference rate not found for the given date"
    ):
        await use_case.execute(user_mock, target_date)

    mock_reference_rate_repo.get_by_date.assert_called_once_with(target_date=target_date)


async def test_income_rounded_to_two_decimal_places(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bondholders: list[Mock],
    reference_rate_mock: Mock,
    bond_entity_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        mbh.bond_id: bond_entity_mock for mbh in mock_bondholders
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    # Calculator returns high-precision value — use case must round it
    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert next(iter(result.data.values())) == Decimal("29.16")
    assert str(next(iter(result.data.values()))) == "29.16"


async def test_different_target_dates(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bondholders: list[Mock],
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_dates = [
        date(2024, 1, 1),
        date(2024, 6, 15),
        date(2024, 12, 31),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        mbh.bond_id: bond_entity_mock for mbh in mock_bondholders
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock

    for target_date in target_dates:
        result = await use_case.execute(user_mock, target_date)
        assert isinstance(result, MonthlyIncomeResponseDTO)


async def test_to_dto_method(use_case: CalculateIncomeUseCase) -> None:
    income_dict = {
        uuid4(): Decimal("100.00"),
        uuid4(): Decimal("200.00"),
        uuid4(): Decimal("300.00"),
    }

    result = use_case._to_dto(income_dict)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == income_dict

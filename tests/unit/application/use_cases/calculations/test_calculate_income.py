from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.dto.calculations import MonthlyIncomeResponseDTO
from src.application.use_cases.calculations.calculate_income import (
    CalculateIncomeUseCase,
)
from src.domain.exceptions import NotFoundError


@pytest.fixture
def use_case(
    mock_bh_income_calculator: Mock,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> CalculateIncomeUseCase:
    return CalculateIncomeUseCase(
        bh_income_calculator=mock_bh_income_calculator,
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


async def test_happy_path(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)
    expected_income: Decimal = Decimal("123.45")

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == [expected_income]

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_mock.id)
    mock_bond_repo.fetch_dict_from_bondholders.assert_called_once_with(
        bondholders=[bondholder_entity_mock]
    )
    mock_reference_rate_repo.get_by_date.assert_called_once_with(
        target_date=target_date
    )
    mock_bh_income_calculator.calculate_monthly_bh_income.assert_called_once_with(
        bondholder=bondholder_entity_mock,
        bond=bond_entity_mock,
        reference_rate=reference_rate_mock,
        day=target_date,
    )


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
    bondholder_entity_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {}

    with pytest.raises(NotFoundError, match="Bonds not found"):
        await use_case.execute(user_mock, target_date)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_mock.id)
    mock_bond_repo.fetch_dict_from_bondholders.assert_called_once_with(
        bondholders=[bondholder_entity_mock]
    )


async def test_reference_rate_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = None

    with pytest.raises(
        NotFoundError, match="Reference rate not found for the given date"
    ):
        await use_case.execute(user_mock, target_date)

    mock_reference_rate_repo.get_by_date.assert_called_once_with(
        target_date=target_date
    )


async def test_multiple_bondholders(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    bh1, bh2 = Mock(), Mock()
    bh1.bond_id = uuid4()
    bh2.bond_id = uuid4()

    bond1, bond2 = Mock(), Mock()

    mock_bondholder_repo.get_all.return_value = [bh1, bh2]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bh1.bond_id: bond1,
        bh2.bond_id: bond2,
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.side_effect = [
        Decimal("100.00"),
        Decimal("200.00"),
    ]

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == [Decimal("100.00"), Decimal("200.00")]
    assert mock_bh_income_calculator.calculate_monthly_bh_income.call_count == 2


async def test_zero_income(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = Decimal("0.00")

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == [Decimal("0.00")]


async def test_income_rounded_to_two_decimal_places(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    # Calculator returns high-precision value — use case must round it
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = Decimal(
        "123.456789"
    )

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == [Decimal("123.46")]
    assert str(result.data[0]) == "123.46"


async def test_large_income(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_date: date = date(2024, 6, 15)
    expected_income: Decimal = Decimal("999999.99")

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(user_mock, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == [expected_income]


async def test_different_target_dates(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
    user_mock: Mock,
) -> None:
    target_dates = [
        date(2024, 1, 1),
        date(2024, 6, 15),
        date(2024, 12, 31),
    ]

    mock_bondholder_repo.get_all.return_value = [bondholder_entity_mock]
    mock_bond_repo.fetch_dict_from_bondholders.return_value = {
        bondholder_entity_mock.bond_id: bond_entity_mock
    }
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = Decimal(
        "100.00"
    )

    for target_date in target_dates:
        result = await use_case.execute(user_mock, target_date)

        assert isinstance(result, MonthlyIncomeResponseDTO)
        assert (
            mock_bh_income_calculator.calculate_monthly_bh_income.call_args[1]["day"]
            == target_date
        )


async def test_to_dto_method(use_case: CalculateIncomeUseCase) -> None:
    income_values = [Decimal("100.00"), Decimal("200.00"), Decimal("300.00")]

    result = use_case._to_dto(income_values)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.data == income_values

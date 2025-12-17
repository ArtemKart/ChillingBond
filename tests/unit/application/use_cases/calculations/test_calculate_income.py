from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

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
) -> None:
    """Test successful income calculation with all data present."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)
    expected_income: Decimal = Decimal("123.45")

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(bondholder_id, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.value == expected_income

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_id)
    mock_bond_repo.get_one.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )
    mock_reference_rate_repo.get_by_date.assert_called_once_with(target_date=target_date)
    mock_bh_income_calculator.calculate_monthly_bh_income.assert_called_once_with(
        bondholder=bondholder_entity_mock,
        bond=bond_entity_mock,
        reference_rate=reference_rate_mock,
        day=target_date,
    )


async def test_bondholder_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
) -> None:
    """Test that NotFoundError is raised when bondholder doesn't exist."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bondholder not found"):
        await use_case.execute(bondholder_id, target_date)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_id)


async def test_bond_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    """Test that NotFoundError is raised when bond doesn't exist."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond not found"):
        await use_case.execute(bondholder_id, target_date)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_id)
    mock_bond_repo.get_one.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )


async def test_reference_rate_not_found(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
) -> None:
    """Test that NotFoundError is raised when reference rate doesn't exist for the given date."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = None

    with pytest.raises(
        NotFoundError, match="Reference rate not found for the given date"
    ):
        await use_case.execute(bondholder_id, target_date)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_id)
    mock_bond_repo.get_one.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )
    mock_reference_rate_repo.get_by_date.assert_called_once_with(target_date=target_date)


async def test_zero_income_calculation(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
) -> None:
    """Test that zero income is handled correctly."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)
    expected_income: Decimal = Decimal("0.00")

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(bondholder_id, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.value == Decimal("0.00")


async def test_large_income_calculation(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
) -> None:
    """Test calculation with large income values."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)
    expected_income: Decimal = Decimal("999999.99")

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(bondholder_id, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.value == expected_income


async def test_to_dto_method(use_case: CalculateIncomeUseCase) -> None:
    """Test the _to_dto static method."""
    income_value = Decimal("456.78")

    result = use_case._to_dto(income_value)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.value == income_value


async def test_different_target_dates(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
) -> None:
    """Test that different target dates are correctly passed to the calculator."""
    bondholder_id: UUID = uuid4()
    target_dates = [
        date(2024, 1, 1),
        date(2024, 6, 15),
        date(2024, 12, 31),
    ]
    expected_income: Decimal = Decimal("100.00")

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    for target_date in target_dates:
        result = await use_case.execute(bondholder_id, target_date)

        assert isinstance(result, MonthlyIncomeResponseDTO)
        assert result.value == expected_income

        # Verify the calculator was called with the correct date
        assert (
            mock_bh_income_calculator.calculate_monthly_bh_income.call_args[1]["day"]
            == target_date
        )


async def test_precision_of_decimal_values(
    use_case: CalculateIncomeUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
    mock_bh_income_calculator: Mock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    reference_rate_mock: Mock,
) -> None:
    """Test that decimal precision is maintained throughout the calculation."""
    bondholder_id: UUID = uuid4()
    target_date: date = date(2024, 6, 15)
    # Income with many decimal places
    expected_income: Decimal = Decimal("123.456789")

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock
    mock_reference_rate_repo.get_by_date.return_value = reference_rate_mock
    mock_bh_income_calculator.calculate_monthly_bh_income.return_value = expected_income

    result = await use_case.execute(bondholder_id, target_date)

    assert isinstance(result, MonthlyIncomeResponseDTO)
    assert result.value == expected_income
    # Verify exact decimal precision is maintained
    assert str(result.value) == "123.456789"

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest_asyncio

from src.application.dto.bond import BondUpdateDTO, BondDTO
from src.application.use_cases.bond_update import BondUpdateUseCase
from src.domain.exceptions import NotFoundError


@pytest_asyncio.fixture
def use_case(mock_bond_repo: AsyncMock) -> BondUpdateUseCase:
    return BondUpdateUseCase(mock_bond_repo)


@pytest_asyncio.fixture
def sample_bond_update_dto() -> Mock:
    dto = Mock(spec=BondUpdateDTO)
    dto.nominal_value = 200.0
    dto.series = None
    dto.maturity_period = None
    dto.initial_interest_rate = None
    dto.first_interest_period = None
    dto.reference_rate_margin = None
    return dto


async def test_success_with_partial_update(
    use_case: BondUpdateUseCase,
    mock_bond_repo: AsyncMock,
    bond_entity_mock: Mock,
    sample_bond_update_dto: Mock,
) -> None:
    bond_id = uuid4()
    mock_bond_repo.get_one.return_value = bond_entity_mock

    with patch("src.application.use_cases.bond_update.asdict") as mock_asdict:
        mock_asdict.return_value = {
            "nominal_value": sample_bond_update_dto.nominal_value,
            "series": sample_bond_update_dto.series,
            "maturity_period": sample_bond_update_dto.maturity_period,
            "initial_interest_rate": sample_bond_update_dto.initial_interest_rate,
            "first_interest_period": sample_bond_update_dto.first_interest_period,
            "reference_rate_margin": sample_bond_update_dto.reference_rate_margin,
        }
        result = await use_case.execute(sample_bond_update_dto, bond_id)

    assert isinstance(result, BondDTO)
    assert result.nominal_value == sample_bond_update_dto.nominal_value
    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)
    mock_bond_repo.update.assert_called_once_with(bond_entity_mock)
    assert bond_entity_mock.nominal_value == sample_bond_update_dto.nominal_value


async def test_success_with_all_fields_update(
    use_case: BondUpdateUseCase, mock_bond_repo: AsyncMock, bond_entity_mock: Mock
) -> None:
    bond_id = uuid4()

    update_dto = Mock(spec=BondUpdateDTO)
    update_dto.nominal_value = 300.0
    update_dto.series = "ROR1111"
    update_dto.maturity_period = 24
    update_dto.initial_interest_rate = 7.5
    update_dto.first_interest_period = 12
    update_dto.reference_rate_margin = 3.5

    mock_bond_repo.get_one.return_value = bond_entity_mock

    with patch("src.application.use_cases.bond_update.asdict") as mock_asdict:
        mock_asdict.return_value = {
            "nominal_value": update_dto.nominal_value,
            "series": update_dto.series,
            "maturity_period": update_dto.maturity_period,
            "initial_interest_rate": update_dto.initial_interest_rate,
            "first_interest_period": update_dto.first_interest_period,
            "reference_rate_margin": update_dto.reference_rate_margin,
        }

        result = await use_case.execute(update_dto, bond_id)

    assert isinstance(result, BondDTO)
    assert result.nominal_value == update_dto.nominal_value
    assert result.series == update_dto.series
    assert result.maturity_period == update_dto.maturity_period
    assert result.initial_interest_rate == update_dto.initial_interest_rate
    assert result.first_interest_period == update_dto.first_interest_period
    assert result.reference_rate_margin == update_dto.reference_rate_margin
    mock_bond_repo.update.assert_called_once_with(bond_entity_mock)


async def test_success_with_no_updates(
    use_case: BondUpdateUseCase, mock_bond_repo: AsyncMock, bond_entity_mock: Mock
) -> None:
    bond_id = uuid4()

    update_dto = Mock(spec=BondUpdateDTO)

    mock_bond_repo.get_one.return_value = bond_entity_mock

    with patch("src.application.use_cases.bond_update.asdict") as mock_asdict:
        mock_asdict.return_value = {
            "nominal_value": None,
            "series": None,
            "maturity_period": None,
            "initial_interest_rate": None,
            "first_interest_period": None,
            "reference_rate_margin": None,
        }

        result = await use_case.execute(update_dto, bond_id)

    assert isinstance(result, BondDTO)

    assert result.nominal_value == bond_entity_mock.nominal_value
    assert result.series == bond_entity_mock.series
    mock_bond_repo.update.assert_called_once_with(bond_entity_mock)


async def test_bond_not_found(
    use_case: BondUpdateUseCase, mock_bond_repo: AsyncMock, sample_bond_update_dto: Mock
) -> None:
    bond_id = uuid4()

    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond not found"):
        await use_case.execute(sample_bond_update_dto, bond_id)

    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)
    mock_bond_repo.update.assert_not_called()


async def test_filters_out_none_values(
    use_case: BondUpdateUseCase, mock_bond_repo: AsyncMock, bond_entity_mock: Mock
) -> None:
    bond_id = uuid4()
    maturity_period_before = bond_entity_mock.maturity_period
    update_dto = Mock(spec=BondUpdateDTO)

    mock_bond_repo.get_one.return_value = bond_entity_mock

    with patch("src.application.use_cases.bond_update.asdict") as mock_asdict:
        mock_asdict.return_value = {
            "nominal_value": 5000.0,
            "series": None,
            "maturity_period": 0,
            "initial_interest_rate": None,
            "first_interest_period": None,
            "reference_rate_margin": None,
        }

        await use_case.execute(update_dto, bond_id)

    assert bond_entity_mock.nominal_value == 5000.0
    assert bond_entity_mock.maturity_period == maturity_period_before


async def test_preserves_unchanged_fields(
    use_case: BondUpdateUseCase, mock_bond_repo: AsyncMock, bond_entity_mock: Mock
) -> None:
    bond_id = uuid4()
    original_maturity = bond_entity_mock.maturity_period
    original_rate = bond_entity_mock.initial_interest_rate

    update_dto = Mock(spec=BondUpdateDTO)

    mock_bond_repo.get_one.return_value = bond_entity_mock

    with patch("src.application.use_cases.bond_update.asdict") as mock_asdict:
        mock_asdict.return_value = {
            "nominal_value": 4000.0,
            "series": None,
            "maturity_period": None,
            "initial_interest_rate": None,
            "first_interest_period": None,
            "reference_rate_margin": None,
        }

        result = await use_case.execute(update_dto, bond_id)

    assert result.nominal_value == 4000.0
    assert result.maturity_period == original_maturity
    assert result.initial_interest_rate == original_rate


async def test_to_dto_creates_correct_dto(
    use_case: BondUpdateUseCase, bond_entity_mock: Mock
) -> None:
    result = use_case._to_dto(bond_entity_mock)

    assert isinstance(result, BondDTO)
    assert result.id == bond_entity_mock.id
    assert result.nominal_value == bond_entity_mock.nominal_value
    assert result.series == bond_entity_mock.series
    assert result.maturity_period == bond_entity_mock.maturity_period
    assert result.initial_interest_rate == bond_entity_mock.initial_interest_rate
    assert result.first_interest_period == bond_entity_mock.first_interest_period
    assert result.reference_rate_margin == bond_entity_mock.reference_rate_margin

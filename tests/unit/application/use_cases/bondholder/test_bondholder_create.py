import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import date

from src.application.use_cases.bondholder.bondholder_create import (
    BondHolderCreateUseCase,
)
from src.application.dto.bond import BondCreateDTO
from src.application.dto.bondholder import BondHolderCreateDTO, BondHolderDTO
from src.domain.entities.bond import Bond as BondEntity
from src.domain.entities.bondholder import BondHolder as BondHolderEntity


@pytest.fixture
async def use_case(
    mock_bond_repo: AsyncMock, mock_bondholder_repo: AsyncMock
) -> BondHolderCreateUseCase:
    return BondHolderCreateUseCase(
        bond_repo=mock_bond_repo, bondholder_repo=mock_bondholder_repo
    )


@pytest.fixture
async def bondholder_create_dto() -> BondHolderCreateDTO:
    return BondHolderCreateDTO(
        user_id=uuid4(),
        quantity=50,
        purchase_date=date.today(),
    )


@pytest.fixture
async def bond_create_dto() -> BondCreateDTO:
    return BondCreateDTO(
        series="ROR1602",
        nominal_value=100.0,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )


@pytest.fixture
async def existing_bond() -> BondEntity:
    return BondEntity(
        id=uuid4(),
        series="ROR1602",
        nominal_value=100.0,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )


@pytest.fixture
async def sample_bondholder_dto() -> BondHolderDTO:
    return BondHolderDTO(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=50,
        purchase_date=date.today(),
        series="ROR1602",
        nominal_value=100.0,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )


async def test_with_existing_bond(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bondholder_create_dto: BondHolderCreateDTO,
    bond_create_dto: BondCreateDTO,
    existing_bond: BondEntity,
    sample_bondholder_dto: BondHolderDTO,
) -> None:
    mock_bond_repo.get_by_series.return_value = existing_bond
    mock_bondholder_repo.write.return_value = Mock(spec=BondHolderEntity)
    use_case.to_dto = AsyncMock(return_value=sample_bondholder_dto)

    result = await use_case.execute(bondholder_create_dto, bond_create_dto)

    mock_bond_repo.get_by_series.assert_called_once_with(bond_create_dto.series)
    mock_bond_repo.write.assert_not_called()

    mock_bondholder_repo.write.assert_called_once()
    created_bondholder = mock_bondholder_repo.write.call_args[0][0]
    assert created_bondholder.bond_id == existing_bond.id
    assert created_bondholder.user_id == bondholder_create_dto.user_id
    assert created_bondholder.quantity == bondholder_create_dto.quantity
    assert created_bondholder.purchase_date == bondholder_create_dto.purchase_date

    use_case.to_dto.assert_called_once()
    assert result == sample_bondholder_dto


async def test_with_new_bond(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bondholder_create_dto: BondHolderCreateDTO,
    bond_create_dto: BondCreateDTO,
    sample_bondholder_dto: BondHolderDTO,
) -> None:
    mock_bond_repo.get_by_series.return_value = None

    new_bond = BondEntity(
        id=uuid4(),
        series=bond_create_dto.series,
        nominal_value=bond_create_dto.nominal_value,
        maturity_period=bond_create_dto.maturity_period,
        initial_interest_rate=bond_create_dto.initial_interest_rate,
        first_interest_period=bond_create_dto.first_interest_period,
        reference_rate_margin=bond_create_dto.reference_rate_margin,
    )
    mock_bond_repo.write.return_value = new_bond

    new_bondholder = Mock(spec=BondHolderEntity)
    mock_bondholder_repo.write.return_value = new_bondholder
    use_case.to_dto = AsyncMock(return_value=sample_bondholder_dto)

    result = await use_case.execute(bondholder_create_dto, bond_create_dto)

    mock_bond_repo.get_by_series.assert_called_once_with(bond_create_dto.series)
    mock_bond_repo.write.assert_called_once()
    created_bond = mock_bond_repo.write.call_args[0][0]
    assert created_bond.series == bond_create_dto.series
    assert created_bond.nominal_value == bond_create_dto.nominal_value
    assert created_bond.maturity_period == bond_create_dto.maturity_period

    mock_bondholder_repo.write.assert_called_once()
    created_bondholder = mock_bondholder_repo.write.call_args[0][0]
    assert created_bondholder.bond_id == new_bond.id
    assert created_bondholder.user_id == bondholder_create_dto.user_id

    use_case.to_dto.assert_called_once_with(bondholder=new_bondholder, bond=new_bond)
    assert result == sample_bondholder_dto


async def test_with_zero_quantity(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bond_create_dto: BondCreateDTO,
    existing_bond: BondEntity,
) -> None:
    bondholder_dto = BondHolderCreateDTO(
        user_id=uuid4(),
        quantity=0,
        purchase_date=date.today(),
    )
    mock_bond_repo.get_by_series.return_value = existing_bond
    mock_bondholder_repo.write.return_value = Mock(spec=BondHolderEntity)

    await use_case.execute(bondholder_dto, bond_create_dto)

    created_bondholder = mock_bondholder_repo.write.call_args[0][0]
    assert created_bondholder.quantity == 0


async def test_with_large_quantity(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bond_create_dto: BondCreateDTO,
    existing_bond: BondEntity,
) -> None:
    bondholder_dto = BondHolderCreateDTO(
        user_id=uuid4(),
        quantity=1000000,
        purchase_date=date.today(),
    )
    mock_bond_repo.get_by_series.return_value = existing_bond
    mock_bondholder_repo.write.return_value = Mock(spec=BondHolderEntity)

    await use_case.execute(bondholder_dto, bond_create_dto)

    created_bondholder = mock_bondholder_repo.write.call_args[0][0]
    assert created_bondholder.quantity == 1000000


async def test_preserves_all_bond_dto_fields(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bondholder_create_dto: BondHolderCreateDTO,
    bond_create_dto: BondCreateDTO,
) -> None:
    mock_bond_repo.get_by_series.return_value = None

    created_bond_from_write = BondEntity(
        id=uuid4(),
        series=bond_create_dto.series,
        nominal_value=bond_create_dto.nominal_value,
        maturity_period=bond_create_dto.maturity_period,
        initial_interest_rate=bond_create_dto.initial_interest_rate,
        first_interest_period=bond_create_dto.first_interest_period,
        reference_rate_margin=bond_create_dto.reference_rate_margin,
    )
    mock_bond_repo.write.return_value = created_bond_from_write

    created_bondholder_from_write = BondHolderEntity(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=bondholder_create_dto.user_id,
        quantity=bondholder_create_dto.quantity,
        purchase_date=bondholder_create_dto.purchase_date,
    )
    mock_bondholder_repo.write.return_value = created_bondholder_from_write

    mock_dto = BondHolderDTO(
        id=created_bondholder_from_write.id,
        bond_id=created_bond_from_write.id,
        user_id=uuid4(),
        quantity=50,
        purchase_date=date.today(),
        series="ROR1206",
        nominal_value=100.0,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0.0,
    )
    use_case.to_dto = AsyncMock(return_value=mock_dto)

    await use_case.execute(bondholder_create_dto, bond_create_dto)

    created_bond = mock_bond_repo.write.call_args[0][0]
    assert created_bond.series == bond_create_dto.series
    assert created_bond.nominal_value == bond_create_dto.nominal_value
    assert created_bond.maturity_period == bond_create_dto.maturity_period
    assert created_bond.initial_interest_rate == bond_create_dto.initial_interest_rate
    assert created_bond.first_interest_period == bond_create_dto.first_interest_period
    assert created_bond.reference_rate_margin == bond_create_dto.reference_rate_margin


async def test_preserves_all_bondholder_dto_fields(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bondholder_create_dto: BondHolderCreateDTO,
    bond_create_dto: BondCreateDTO,
    existing_bond: BondEntity,
) -> None:
    mock_bond_repo.get_by_series.return_value = existing_bond
    mock_bondholder_repo.write.return_value = Mock(spec=BondHolderEntity)

    await use_case.execute(bondholder_create_dto, bond_create_dto)

    created_bondholder = mock_bondholder_repo.write.call_args[0][0]
    assert created_bondholder.user_id == bondholder_create_dto.user_id
    assert created_bondholder.quantity == bondholder_create_dto.quantity
    assert created_bondholder.purchase_date == bondholder_create_dto.purchase_date
    assert created_bondholder.bond_id == existing_bond.id


async def test_calls_to_dto_with_correct_params(
    use_case: BondHolderCreateUseCase,
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    bondholder_create_dto: BondHolderCreateDTO,
    bond_create_dto: BondCreateDTO,
    existing_bond: BondEntity,
) -> None:
    mock_bond_repo.get_by_series.return_value = existing_bond
    created_bondholder = Mock(spec=BondHolderEntity)
    mock_bondholder_repo.write.return_value = created_bondholder
    use_case.to_dto = AsyncMock()

    await use_case.execute(bondholder_create_dto, bond_create_dto)

    call_args = use_case.to_dto.call_args
    assert call_args[1]["bond"] == existing_bond

    bondholder_arg = call_args[1]["bondholder"]
    assert bondholder_arg.bond_id == existing_bond.id
    assert bondholder_arg.user_id == bondholder_create_dto.user_id

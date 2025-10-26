from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date

from src.application.dto.bondholder import BondHolderChangeQuantityDTO, BondHolderDTO
from src.application.use_cases.bondholder.bondholder_add import (
    BondAddToBondHolderUseCase,
)
from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder
from src.domain.exceptions import NotFoundError, InvalidTokenError


@pytest.fixture
async def use_case(
    mock_bond_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
) -> BondAddToBondHolderUseCase:
    return BondAddToBondHolderUseCase(
        bond_repo=mock_bond_repo,
        user_repo=mock_user_repo,
        bondholder_repo=mock_bondholder_repo,
    )


@pytest.fixture
async def sample_dto() -> BondHolderChangeQuantityDTO:
    return BondHolderChangeQuantityDTO(
        id=uuid4(),
        user_id=uuid4(),
        quantity=10,
        is_positive=True,
    )


@pytest.fixture
async def sample_bondholder() -> Mock:
    bondholder = Mock(spec=BondHolder)
    bondholder.id = uuid4()
    bondholder.bond_id = uuid4()
    bondholder.user_id = uuid4()
    bondholder.quantity = 50
    bondholder.purchase_date = date.today()
    bondholder.add_quantity = AsyncMock()
    bondholder.reduce_quantity = AsyncMock()
    return bondholder


@pytest.fixture
async def sample_bond() -> Mock:
    bond = Mock(spec=Bond)
    bond.id = uuid4()
    bond.series = "ROR1602"
    bond.nominal_value = 100
    bond.maturity_period = 12
    bond.initial_interest_rate = 4.75
    bond.first_interest_period = 1
    bond.reference_rate_margin = 0
    return bond


async def test_add_quantity_success(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
    sample_bondholder: Mock,
    sample_bond: Mock,
) -> None:
    common_user_id = uuid4()
    sample_dto.user_id = common_user_id
    sample_bondholder.user_id = common_user_id

    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = sample_bond

    result = await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)
    sample_bondholder.add_quantity.assert_called_once_with(sample_dto.quantity)
    sample_bondholder.reduce_quantity.assert_not_called()
    mock_bondholder_repo.update.assert_called_once_with(sample_bondholder)
    mock_bond_repo.get_one.assert_called_once_with(sample_bondholder.bond_id)
    assert isinstance(result, BondHolderDTO)


async def test_reduce_quantity_success(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_bondholder: Mock,
    sample_bond: Mock,
) -> None:
    common_user_id = uuid4()
    sample_bondholder.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(), user_id=common_user_id, quantity=5, is_positive=False
    )
    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = sample_bond

    result = await use_case.execute(dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=dto.id)
    sample_bondholder.reduce_quantity.assert_called_once_with(dto.quantity)
    sample_bondholder.add_quantity.assert_not_called()
    mock_bondholder_repo.update.assert_called_once_with(sample_bondholder)
    mock_bond_repo.get_one.assert_called_once_with(sample_bondholder.bond_id)
    assert isinstance(result, BondHolderDTO)


async def test_bondholder_not_found(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
) -> None:
    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond holder not found"):
        await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)


async def test_user_not_authenticated(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    sample_bondholder: Mock,
) -> None:
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(), user_id=uuid4(), quantity=10, is_positive=True
    )
    mock_bondholder_repo.get_one.return_value = sample_bondholder

    with pytest.raises(InvalidTokenError, match="Not authenticated"):
        await use_case.execute(dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=dto.id)
    sample_bondholder.add_quantity.assert_not_called()
    sample_bondholder.reduce_quantity.assert_not_called()


async def test_bond_not_found(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
    sample_bondholder: Mock,
) -> None:
    common_user_id = uuid4()
    sample_dto.user_id = common_user_id
    sample_bondholder.user_id = common_user_id

    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond connected to BondHolder not found"):
        await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)
    sample_bondholder.add_quantity.assert_called_once_with(sample_dto.quantity)
    mock_bondholder_repo.update.assert_called_once_with(sample_bondholder)
    mock_bond_repo.get_one.assert_called_once_with(sample_bondholder.bond_id)


async def test_calls_to_dto_method(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
    sample_bondholder: Mock,
    sample_bond: Mock,
) -> None:
    common_user_id = uuid4()
    sample_dto.user_id = common_user_id
    sample_bondholder.user_id = common_user_id

    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = sample_bond

    expected_dto = BondHolderDTO(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        purchase_date=date.today(),
        quantity=100,
        series="ROR1206",
        nominal_value=100,
        maturity_period=12,
        initial_interest_rate=4.75,
        first_interest_period=1,
        reference_rate_margin=0,
    )

    use_case.to_dto = AsyncMock(return_value=expected_dto)

    result = await use_case.execute(sample_dto)

    use_case.to_dto.assert_called_once_with(
        bond=sample_bond, bondholder=sample_bondholder
    )
    assert result == expected_dto


async def test_with_zero_quantity(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_bondholder: Mock,
    sample_bond: Mock,
) -> None:
    common_user_id = uuid4()
    sample_bondholder.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(), user_id=common_user_id, quantity=0, is_positive=True
    )
    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = sample_bond

    result = await use_case.execute(dto)

    sample_bondholder.add_quantity.assert_called_once_with(0)
    assert isinstance(result, BondHolderDTO)


async def test_with_large_quantity(
    use_case: BondAddToBondHolderUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_bondholder: Mock,
    sample_bond: Mock,
) -> None:
    common_user_id = uuid4()
    sample_bondholder.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(),
        user_id=common_user_id,
        quantity=1000000,
        is_positive=True,
    )
    mock_bondholder_repo.get_one.return_value = sample_bondholder
    mock_bondholder_repo.update.return_value = sample_bondholder
    mock_bond_repo.get_one.return_value = sample_bond

    result = await use_case.execute(dto)

    sample_bondholder.add_quantity.assert_called_once_with(1000000)
    assert isinstance(result, BondHolderDTO)

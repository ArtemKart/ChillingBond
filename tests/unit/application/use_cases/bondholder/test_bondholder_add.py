from decimal import Decimal
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date

from src.application.dto.bondholder import BondHolderChangeQuantityDTO, BondHolderDTO
from src.application.use_cases.bondholder.bh_add import (
    ChangeBondHolderQuantityUseCase,
)
from src.domain.exceptions import NotFoundError, InvalidTokenError


@pytest.fixture
async def use_case(
    mock_bond_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
) -> ChangeBondHolderQuantityUseCase:
    return ChangeBondHolderQuantityUseCase(
        bond_repo=mock_bond_repo,
        user_repo=mock_user_repo,
        bondholder_repo=mock_bondholder_repo,
    )


@pytest.fixture
async def sample_dto() -> BondHolderChangeQuantityDTO:
    return BondHolderChangeQuantityDTO(
        id=uuid4(),
        user_id=uuid4(),
        new_quantity=10,
    )


async def test_change_quantity_success(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
) -> None:
    common_user_id = uuid4()
    bondholder_entity_mock.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(), user_id=common_user_id, new_quantity=5
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    result = await use_case.execute(dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=dto.id)
    bondholder_entity_mock.change_quantity.assert_called_once_with(dto.new_quantity)
    mock_bondholder_repo.update.assert_called_once_with(bondholder_entity_mock)
    mock_bond_repo.get_one.assert_called_once_with(bondholder_entity_mock.bond_id)
    assert isinstance(result, BondHolderDTO)


async def test_bondholder_not_found(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
) -> None:
    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond holder not found"):
        await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)


async def test_user_not_authenticated(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(),
        user_id=uuid4(),
        new_quantity=10,
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock

    with pytest.raises(InvalidTokenError, match="Not authenticated"):
        await use_case.execute(dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=dto.id)
    bondholder_entity_mock.change_quantity.assert_not_called()


async def test_bond_not_found(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
    bondholder_entity_mock: Mock,
) -> None:
    common_user_id = uuid4()
    sample_dto.user_id = common_user_id
    bondholder_entity_mock.user_id = common_user_id

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond connected to BondHolder not found"):
        await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)
    bondholder_entity_mock.change_quantity.assert_called_once_with(
        sample_dto.new_quantity
    )
    mock_bondholder_repo.update.assert_called_once_with(bondholder_entity_mock)
    mock_bond_repo.get_one.assert_called_once_with(bondholder_entity_mock.bond_id)


async def test_calls_to_dto_method(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderChangeQuantityDTO,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
) -> None:
    common_user_id = uuid4()
    sample_dto.user_id = common_user_id
    bondholder_entity_mock.user_id = common_user_id

    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    expected_dto = BondHolderDTO(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        purchase_date=date.today(),
        quantity=100,
        series="ROR1206",
        nominal_value=Decimal("100"),
        maturity_period=12,
        initial_interest_rate=Decimal("4.75"),
        first_interest_period=1,
        reference_rate_margin=Decimal("0"),
    )

    use_case.to_dto = Mock(return_value=expected_dto)

    result = await use_case.execute(sample_dto)

    use_case.to_dto.assert_called_once_with(
        bond=bond_entity_mock, bondholder=bondholder_entity_mock
    )
    assert result == expected_dto


async def test_with_zero_quantity(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
) -> None:
    common_user_id = uuid4()
    bondholder_entity_mock.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(), user_id=common_user_id, new_quantity=0
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    result = await use_case.execute(dto)

    bondholder_entity_mock.change_quantity.assert_called_once_with(0)
    assert isinstance(result, BondHolderDTO)


async def test_with_large_quantity(
    use_case: ChangeBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
) -> None:
    common_user_id = uuid4()
    bondholder_entity_mock.user_id = common_user_id
    dto = BondHolderChangeQuantityDTO(
        id=uuid4(),
        user_id=common_user_id,
        new_quantity=1000000,
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    result = await use_case.execute(dto)

    bondholder_entity_mock.change_quantity.assert_called_once_with(1000000)
    assert isinstance(result, BondHolderDTO)

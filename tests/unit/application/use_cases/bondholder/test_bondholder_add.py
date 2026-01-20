from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.dto.bondholder import BondHolderDTO, BondHolderUpdateQuantityDTO
from src.application.dto.user import UserDTO
from src.application.use_cases.bondholder.bh_update_quantity import (
    UpdateBondHolderQuantityUseCase,
)
from src.domain.exceptions import AuthorizationError, NotFoundError


@pytest.fixture
async def use_case(
    mock_bond_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
) -> UpdateBondHolderQuantityUseCase:
    return UpdateBondHolderQuantityUseCase(
        bond_repo=mock_bond_repo,
        bondholder_repo=mock_bondholder_repo,
    )


@pytest.fixture
async def sample_dto(user_dto: UserDTO) -> BondHolderUpdateQuantityDTO:
    return BondHolderUpdateQuantityDTO(
        id=uuid4(),
        user=user_dto,
        new_quantity=10,
    )


async def test_change_quantity_success(
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    bondholder_entity_mock.user_id = user_dto.id
    dto = BondHolderUpdateQuantityDTO(id=uuid4(), user=user_dto, new_quantity=5)
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
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    sample_dto: BondHolderUpdateQuantityDTO,
) -> None:
    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond holder not found"):
        await use_case.execute(sample_dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=sample_dto.id)


async def test_user_not_authenticated(
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    dto = BondHolderUpdateQuantityDTO(
        id=uuid4(),
        user=user_dto,
        new_quantity=10,
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock

    with pytest.raises(AuthorizationError, match="Permission denied"):
        await use_case.execute(dto)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=dto.id)
    bondholder_entity_mock.change_quantity.assert_not_called()


async def test_bond_not_found(
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderUpdateQuantityDTO,
    bondholder_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    sample_dto.user = user_dto
    bondholder_entity_mock.user_id = user_dto.id

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
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    sample_dto: BondHolderUpdateQuantityDTO,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    sample_dto.user = user_dto
    bondholder_entity_mock.user_id = user_dto.id

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
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    bondholder_entity_mock.user_id = user_dto.id
    dto = BondHolderUpdateQuantityDTO(id=uuid4(), user=user_dto, new_quantity=0)
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    result = await use_case.execute(dto)

    bondholder_entity_mock.change_quantity.assert_called_once_with(0)
    assert isinstance(result, BondHolderDTO)


async def test_with_large_quantity(
    use_case: UpdateBondHolderQuantityUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    bond_entity_mock: Mock,
    user_dto: UserDTO,
) -> None:
    bondholder_entity_mock.user_id = user_dto.id
    dto = BondHolderUpdateQuantityDTO(
        id=uuid4(),
        user=user_dto,
        new_quantity=1000000,
    )
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.update.return_value = bondholder_entity_mock
    mock_bond_repo.get_one.return_value = bond_entity_mock

    result = await use_case.execute(dto)

    bondholder_entity_mock.change_quantity.assert_called_once_with(1000000)
    assert isinstance(result, BondHolderDTO)

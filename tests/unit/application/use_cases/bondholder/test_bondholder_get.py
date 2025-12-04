import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.bondholder_get import BondHolderGetUseCase
from src.domain.exceptions import NotFoundError, AuthorizationError


@pytest.fixture
def use_case(
    mock_bondholder_repo: AsyncMock, mock_bond_repo: AsyncMock
) -> BondHolderGetUseCase:
    return BondHolderGetUseCase(mock_bondholder_repo, mock_bond_repo)


async def test_happy_path(
    use_case: BondHolderGetUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    bondholder_id: UUID = uuid4()
    user_id: UUID = uuid4()
    bond_id: UUID = uuid4()

    mock_bondholder = Mock()
    mock_bondholder.user_id = user_id
    mock_bondholder.bond_id = bond_id

    mock_bond = Mock()

    expected_dto = Mock(spec=BondHolderDTO)

    mock_bondholder_repo.get_one.return_value = mock_bondholder
    mock_bond_repo.get_one.return_value = mock_bond
    use_case.to_dto = Mock(return_value=expected_dto)

    result = await use_case.execute(bondholder_id, user_id)

    assert result == expected_dto
    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id)
    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)
    use_case.to_dto.assert_called_once_with(bondholder=mock_bondholder, bond=mock_bond)


async def test_bondholder_not_found(
    use_case: BondHolderGetUseCase, mock_bondholder_repo: AsyncMock
) -> None:
    bondholder_id: UUID = uuid4()
    user_id: UUID = uuid4()

    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="BondHolder not found"):
        await use_case.execute(bondholder_id, user_id)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id)


async def test_user_not_owner(
    use_case: BondHolderGetUseCase, mock_bondholder_repo: AsyncMock
) -> None:
    bondholder_id: UUID = uuid4()
    user_id: UUID = uuid4()
    different_user_id: UUID = uuid4()

    mock_bondholder = Mock()
    mock_bondholder.user_id = different_user_id

    mock_bondholder_repo.get_one.return_value = mock_bondholder

    with pytest.raises(AuthorizationError, match="Permission denied"):
        await use_case.execute(bondholder_id, user_id)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id)


async def test_bond_not_found(
    use_case: BondHolderGetUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    bondholder_id: UUID = uuid4()
    user_id: UUID = uuid4()
    bond_id: UUID = uuid4()

    mock_bondholder = Mock()
    mock_bondholder.user_id = user_id
    mock_bondholder.bond_id = bond_id

    mock_bondholder_repo.get_one.return_value = mock_bondholder
    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond connected to BondHolder not found"):
        await use_case.execute(bondholder_id, user_id)

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id)
    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)

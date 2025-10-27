import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest_asyncio

from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.bondholder_get import BondHolderGetAllUseCase
from src.domain.exceptions import NotFoundError


@pytest_asyncio.fixture
def use_case(
    mock_bondholder_repo: AsyncMock, mock_bond_repo: AsyncMock
) -> BondHolderGetAllUseCase:
    return BondHolderGetAllUseCase(mock_bondholder_repo, mock_bond_repo)


async def test_success_with_multiple_bondholders(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_ids = [uuid4(), uuid4(), uuid4()]

    mock_bondholders = [
        Mock(bond_id=bond_ids[0]),
        Mock(bond_id=bond_ids[1]),
        Mock(bond_id=bond_ids[2]),
    ]

    mock_bonds = [Mock(), Mock(), Mock()]
    expected_dtos = [
        Mock(spec=BondHolderDTO),
        Mock(spec=BondHolderDTO),
        Mock(spec=BondHolderDTO),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_one.side_effect = mock_bonds
    use_case.to_dto = AsyncMock(side_effect=expected_dtos)

    result = await use_case.execute(user_id)

    assert result == expected_dtos
    assert len(result) == 3
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    assert mock_bond_repo.get_one.call_count == 3
    mock_bond_repo.get_one.assert_any_call(bond_id=bond_ids[0])
    mock_bond_repo.get_one.assert_any_call(bond_id=bond_ids[1])
    mock_bond_repo.get_one.assert_any_call(bond_id=bond_ids[2])
    assert use_case.to_dto.call_count == 3


async def test_success_with_empty_list(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()

    mock_bondholder_repo.get_all.return_value = []

    result = await use_case.execute(user_id)

    assert result == []
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    mock_bond_repo.get_one.assert_not_called()


async def test_success_with_single_bondholder(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_id = uuid4()

    mock_bondholder = Mock(bond_id=bond_id)
    mock_bond = Mock()
    expected_dto = Mock(spec=BondHolderDTO)

    mock_bondholder_repo.get_all.return_value = [mock_bondholder]
    mock_bond_repo.get_one.return_value = mock_bond
    use_case.to_dto = AsyncMock(return_value=expected_dto)

    result = await use_case.execute(user_id)

    assert result == [expected_dto]
    assert len(result) == 1
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)
    use_case.to_dto.assert_called_once_with(bondholder=mock_bondholder, bond=mock_bond)


async def test_bond_not_found_first_item(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_id = uuid4()

    mock_bondholder = Mock(bond_id=bond_id)

    mock_bondholder_repo.get_all.return_value = [mock_bondholder]
    mock_bond_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bond connected to BondHolder not found"):
        await use_case.execute(user_id)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    mock_bond_repo.get_one.assert_called_once_with(bond_id=bond_id)


async def test_bond_not_found_middle_item(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_ids = [uuid4(), uuid4(), uuid4()]

    mock_bondholders = [
        Mock(bond_id=bond_ids[0]),
        Mock(bond_id=bond_ids[1]),
        Mock(bond_id=bond_ids[2]),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_one.side_effect = [Mock(), None, Mock()]
    use_case.to_dto = AsyncMock()

    with pytest.raises(NotFoundError, match="Bond connected to BondHolder not found"):
        await use_case.execute(user_id)

    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    assert mock_bond_repo.get_one.call_count == 2
    assert use_case.to_dto.call_count == 1


async def test_preserves_order(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_ids = [uuid4(), uuid4(), uuid4()]

    mock_bondholders = [
        Mock(bond_id=bond_ids[0], name="first"),
        Mock(bond_id=bond_ids[1], name="second"),
        Mock(bond_id=bond_ids[2], name="third"),
    ]

    mock_bonds = [
        Mock(name="bond1"),
        Mock(name="bond2"),
        Mock(name="bond3"),
    ]

    expected_dtos = [
        Mock(spec=BondHolderDTO, id=1),
        Mock(spec=BondHolderDTO, id=2),
        Mock(spec=BondHolderDTO, id=3),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_one.side_effect = mock_bonds
    use_case.to_dto = AsyncMock(side_effect=expected_dtos)

    result = await use_case.execute(user_id)

    assert result == expected_dtos
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3

    calls = use_case.to_dto.call_args_list
    assert calls[0].kwargs == {"bondholder": mock_bondholders[0], "bond": mock_bonds[0]}
    assert calls[1].kwargs == {"bondholder": mock_bondholders[1], "bond": mock_bonds[1]}
    assert calls[2].kwargs == {"bondholder": mock_bondholders[2], "bond": mock_bonds[2]}

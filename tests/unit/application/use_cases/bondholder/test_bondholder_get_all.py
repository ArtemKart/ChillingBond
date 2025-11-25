from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
import pytest_asyncio

from src.adapters.outbound.database.models import BondHolder
from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.bondholder_get import BondHolderGetAllUseCase
from src.domain.entities.bond import Bond
from src.domain.exceptions import NotFoundError


@pytest_asyncio.fixture
async def use_case(mock_bondholder_repo: AsyncMock, mock_bond_repo: AsyncMock) -> BondHolderGetAllUseCase:
    return BondHolderGetAllUseCase(mock_bondholder_repo, mock_bond_repo)


async def test_success_with_multiple_bondholders(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_ids = [uuid4(), uuid4(), uuid4()]

    today = datetime.today()
    mock_bondholders = [
        Mock(bond_id=bond_ids[0], purchase_date=today - timedelta(days=1)),
        Mock(bond_id=bond_ids[1], purchase_date=today - timedelta(days=5)),
        Mock(bond_id=bond_ids[2], purchase_date=today - timedelta(days=3)),
    ]

    mock_bonds = [Mock(), Mock(), Mock()]
    expected_dtos = [
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=1)),
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=3)),
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=5)),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_one.side_effect = mock_bonds
    use_case.to_dto = Mock(side_effect=expected_dtos)

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

    today = datetime.today()
    mock_bondholder = Mock(bond_id=bond_id)
    mock_bond = Mock()
    expected_dto = Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=1))

    mock_bondholder_repo.get_all.return_value = [mock_bondholder]
    mock_bond_repo.get_one.return_value = mock_bond
    use_case.to_dto = Mock(return_value=expected_dto)

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
    bond_id = uuid4()

    bondholders = [
        BondHolder(
            id=uuid4(),
            user_id=user_id,
            bond_id=bond_id,
            quantity=1,
            purchase_date=date(2025, 1, 15),
            last_update=datetime.today() - timedelta(days=1),
        ),
        BondHolder(
            id=uuid4(),
            user_id=user_id,
            bond_id=bond_id,
            quantity=1,
            purchase_date=date(2025, 11, 20),
            last_update=datetime.today() - timedelta(days=1),
        ),
        BondHolder(
            id=uuid4(),
            user_id=user_id,
            bond_id=bond_id,
            quantity=1,
            purchase_date=date(2025, 6, 1),
            last_update=datetime.today() - timedelta(days=1),
        ),
    ]

    bond = Bond(
        id=bond_id,
        series="001",
        nominal_value=1000.0,
        maturity_period=12,
        initial_interest_rate=5.0,
        first_interest_period=6,
        reference_rate_margin=1.0,
    )

    mock_bondholder_repo.get_all.return_value = bondholders
    mock_bond_repo.get_one.return_value = bond

    result = await use_case.execute(user_id)

    assert result[0].purchase_date == date(2025, 11, 20)
    assert result[1].purchase_date == date(2025, 6, 1)
    assert result[2].purchase_date == date(2025, 1, 15)

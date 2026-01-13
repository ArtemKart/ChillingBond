from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.adapters.outbound.database.models import BondHolder
from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.bh_get import BondHolderGetAllUseCase
from src.domain.entities.bond import Bond


@pytest.fixture
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

    today = datetime.today()
    mock_bondholders = [
        Mock(bond_id=bond_ids[0], purchase_date=today - timedelta(days=1)),
        Mock(bond_id=bond_ids[1], purchase_date=today - timedelta(days=5)),
        Mock(bond_id=bond_ids[2], purchase_date=today - timedelta(days=3)),
    ]

    mock_bonds = [Mock(id=uuid4()), Mock(id=uuid4()), Mock(id=uuid4())]
    expected_dtos = [
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=1)),
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=3)),
        Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=5)),
    ]

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_many.return_value = mock_bonds
    use_case.to_dto = Mock(side_effect=expected_dtos)

    result = await use_case.execute(user_id)

    assert result == expected_dtos
    assert len(result) == 3
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    mock_bond_repo.get_many.assert_called_once()
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
    mock_bond_repo.get_many.assert_not_called()


async def test_success_with_single_bondholder(
    use_case: BondHolderGetAllUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
) -> None:
    user_id = uuid4()
    bond_id = uuid4()

    today = datetime.today()
    mock_bondholders = [Mock(bond_id=bond_id)]
    mock_bonds = [Mock(id=bond_id)]
    expected_dto = Mock(spec=BondHolderDTO, purchase_date=today - timedelta(days=1))

    mock_bondholder_repo.get_all.return_value = mock_bondholders
    mock_bond_repo.get_many.return_value = mock_bonds
    use_case.to_dto = Mock(return_value=expected_dto)

    result = await use_case.execute(user_id)

    assert result == [expected_dto]
    assert len(result) == 1
    mock_bondholder_repo.get_all.assert_called_once_with(user_id=user_id)
    mock_bond_repo.get_many.assert_called_once()
    use_case.to_dto.assert_called_once_with(
        bondholder=mock_bondholders[0], bond=mock_bonds[0]
    )


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

    bonds = [
        Bond(
            id=bond_id,
            series="001",
            nominal_value=Decimal("1000.0"),
            maturity_period=12,
            initial_interest_rate=Decimal("5.0"),
            first_interest_period=6,
            reference_rate_margin=Decimal("1.0"),
        )
    ]

    mock_bondholder_repo.get_all.return_value = bondholders
    mock_bond_repo.get_many.return_value = list(bonds)

    result = await use_case.execute(user_id)

    assert result[0].purchase_date == date(2025, 11, 20)
    assert result[1].purchase_date == date(2025, 6, 1)
    assert result[2].purchase_date == date(2025, 1, 15)

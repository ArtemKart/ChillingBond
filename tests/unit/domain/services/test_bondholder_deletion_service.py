import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


@pytest.fixture
def deletion_service(mock_bondholder_repo: AsyncMock, mock_user_repo: AsyncMock):
    return BondHolderDeletionService(
        bondholder_repo=mock_bondholder_repo,
        bond_repo=mock_user_repo,
    )


@pytest.mark.asyncio
async def test_delete_bondholder_with_remaining_holders(
    deletion_service,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    bond_id = uuid4()
    mock_bondholder_repo.count_by_bond_id.return_value = 2

    await deletion_service.delete_with_cleanup(
        bondholder_id=bondholder_id,
        bond_id=bond_id,
    )

    mock_bondholder_repo.delete.assert_awaited_once_with(bondholder_id=bondholder_id)
    mock_bondholder_repo.count_by_bond_id.assert_awaited_once_with(bond_id=bond_id)
    mock_user_repo.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_last_bondholder_deletes_bond(
    deletion_service,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    bond_id = uuid4()
    mock_bondholder_repo.count_by_bond_id.return_value = 0

    await deletion_service.delete_with_cleanup(
        bondholder_id=bondholder_id,
        bond_id=bond_id,
    )

    mock_bondholder_repo.delete.assert_awaited_once_with(bondholder_id=bondholder_id)
    mock_bondholder_repo.count_by_bond_id.assert_awaited_once_with(bond_id=bond_id)
    mock_user_repo.delete.assert_awaited_once_with(bond_id=bond_id)


@pytest.mark.asyncio
async def test_delete_bondholder_single_holder(
    deletion_service,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    bond_id = uuid4()
    mock_bondholder_repo.count_by_bond_id.return_value = 0

    await deletion_service.delete_with_cleanup(
        bondholder_id=bondholder_id,
        bond_id=bond_id,
    )

    mock_bondholder_repo.delete.assert_awaited_once_with(bondholder_id=bondholder_id)
    mock_bondholder_repo.count_by_bond_id.assert_awaited_once_with(bond_id=bond_id)
    mock_user_repo.delete.assert_awaited_once_with(bond_id=bond_id)


@pytest.mark.asyncio
async def test_delete_calls_in_correct_order(
    deletion_service,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    bond_id = uuid4()
    call_order = []

    async def track_bondholder_delete(*args, **kwargs):
        call_order.append("bondholder_delete")

    async def track_count(*args, **kwargs):
        call_order.append("count")
        return 0

    async def track_bond_delete(*args, **kwargs):
        call_order.append("bond_delete")

    mock_bondholder_repo.delete.side_effect = track_bondholder_delete
    mock_bondholder_repo.count_by_bond_id.side_effect = track_count
    mock_user_repo.delete.side_effect = track_bond_delete

    await deletion_service.delete_with_cleanup(
        bondholder_id=bondholder_id,
        bond_id=bond_id,
    )

    assert call_order == ["bondholder_delete", "count", "bond_delete"]

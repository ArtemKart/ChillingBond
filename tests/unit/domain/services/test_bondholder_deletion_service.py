from unittest.mock import Mock, AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio

from src.domain.exceptions import NotFoundError, AuthorizationError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


@pytest_asyncio.fixture
async def bh_del_service(
    mock_bondholder_repo: BondHolderRepository,
    mock_bond_repo: BondRepository,
) -> BondHolderDeletionService:
    return BondHolderDeletionService(
        bondholder_repo=mock_bondholder_repo,
        bond_repo=mock_bond_repo,
    )


async def test_delete_with_cleanup_bond_has_0_references(
    bh_del_service: BondHolderDeletionService,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    user_id = bondholder_entity_mock.user_id
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.count_by_bond_id.return_value = 0


    await bh_del_service.delete_with_cleanup(
        bondholder_id=bondholder_entity_mock.id, user_id=user_id,
    )

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_entity_mock.id)
    mock_bondholder_repo.delete.assert_called_once_with(bondholder_id=bondholder_entity_mock.id)
    mock_bondholder_repo.count_by_bond_id.assert_called_once_with(bond_id=bondholder_entity_mock.bond_id)
    mock_bond_repo.delete.assert_called_once_with(bond_id=bondholder_entity_mock.bond_id)


async def test_delete_with_cleanup_bond_has_references(
    bh_del_service: BondHolderDeletionService,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    user_id = bondholder_entity_mock.user_id
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.count_by_bond_id.return_value = 1

    await bh_del_service.delete_with_cleanup(
        bondholder_id=bondholder_entity_mock.id, user_id=user_id,
    )

    mock_bondholder_repo.get_one.assert_called_once_with(bondholder_id=bondholder_entity_mock.id)
    mock_bondholder_repo.delete.assert_called_once_with(bondholder_id=bondholder_entity_mock.id)
    mock_bondholder_repo.count_by_bond_id.assert_called_once_with(bond_id=bondholder_entity_mock.bond_id)
    mock_bond_repo.delete.assert_not_called()


async def test_delete_with_cleanup_bondholder_not_found(
    bh_del_service: BondHolderDeletionService,
    mock_bondholder_repo: AsyncMock,
) -> None:
    mock_bondholder_repo.get_one.return_value = None
    with pytest.raises(NotFoundError, match="Bondholder not found"):
        await bh_del_service.delete_with_cleanup(
            bondholder_id=uuid4(), user_id=uuid4(),
        )

async def test_delete_with_cleanup_not_authorized(
    bh_del_service: BondHolderDeletionService,
    bondholder_entity_mock: Mock,
    mock_bondholder_repo: AsyncMock,
) -> None:
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    user_id = uuid4()
    assert bondholder_entity_mock.user_id != user_id

    with pytest.raises(AuthorizationError, match="Permission denied"):
        await bh_del_service.delete_with_cleanup(
            bondholder_id=bondholder_entity_mock.id, user_id=user_id,
        )

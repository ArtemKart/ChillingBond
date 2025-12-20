from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.use_cases.bondholder.bh_delete import (
    BondHolderDeleteUseCase,
)
from src.domain.entities.bondholder import BondHolder
from src.domain.entities.user import User
from src.domain.exceptions import AuthorizationError, NotFoundError


@pytest.fixture
def use_case(
    mock_bondholder_repo: AsyncMock,
    mock_event_publisher: AsyncMock,
    mock_user_repo: AsyncMock,
    bh_del_service_mock: AsyncMock,
) -> BondHolderDeleteUseCase:
    return BondHolderDeleteUseCase(
        bondholder_repo=mock_bondholder_repo,
        event_publisher=mock_event_publisher,
        user_repo=mock_user_repo,
        bh_del_service=bh_del_service_mock,
    )


async def test_delete_bondholder_success(
    use_case: BondHolderDeleteUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_event_publisher: AsyncMock,
    bh_del_service_mock: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    user_id = uuid4()
    bond_id = uuid4()
    user_email = "test@example.com"

    bondholder_mock = Mock(spec=BondHolder)
    bondholder_mock.id = bondholder_id
    bondholder_mock.user_id = user_id
    bondholder_mock.bond_id = bond_id
    bondholder_mock.collect_events.return_value = [Mock(), Mock()]

    user_mock = Mock(spec=User)
    user_mock.email = user_email

    mock_bondholder_repo.get_one.return_value = bondholder_mock
    mock_user_repo.get_one.return_value = user_mock

    await use_case.execute(bondholder_id=bondholder_id, user_id=user_id)

    mock_bondholder_repo.get_one.assert_awaited_once_with(bondholder_id=bondholder_id)
    mock_user_repo.get_one.assert_awaited_once_with(user_id=user_id)
    bondholder_mock.mark_as_deleted.assert_called_once_with(user_email=user_email)
    bh_del_service_mock.delete_with_cleanup.assert_awaited_once_with(
        bondholder_id=bondholder_id, bond_id=bond_id
    )
    mock_event_publisher.publish_all.assert_awaited_once_with(
        bondholder_mock.collect_events.return_value
    )


@pytest.mark.asyncio
async def test_delete_bondholder_not_found(
    use_case: BondHolderDeleteUseCase, mock_bondholder_repo: AsyncMock
) -> None:
    bondholder_id = uuid4()
    user_id = uuid4()
    mock_bondholder_repo.get_one.return_value = None

    with pytest.raises(NotFoundError, match="Bondholder not found"):
        await use_case.execute(bondholder_id=bondholder_id, user_id=user_id)

    mock_bondholder_repo.get_one.assert_awaited_once_with(bondholder_id=bondholder_id)


@pytest.mark.asyncio
async def test_delete_bondholder_wrong_owner(
    use_case: BondHolderDeleteUseCase,
    mock_bondholder_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    user_id = uuid4()
    different_user_id = uuid4()

    bondholder_mock = Mock(spec=BondHolder)
    bondholder_mock.user_id = different_user_id

    mock_bondholder_repo.get_one.return_value = bondholder_mock

    with pytest.raises(AuthorizationError, match="Permission denied"):
        await use_case.execute(bondholder_id=bondholder_id, user_id=user_id)

    mock_bondholder_repo.get_one.assert_awaited_once_with(bondholder_id=bondholder_id)


@pytest.mark.asyncio
async def test_delete_bondholder_user_not_found(
    use_case: BondHolderDeleteUseCase,
    mock_bondholder_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    user_id = uuid4()

    bondholder_mock = Mock(spec=BondHolder)
    bondholder_mock.user_id = user_id

    mock_bondholder_repo.get_one.return_value = bondholder_mock
    mock_user_repo.get_one.return_value = None

    with pytest.raises(AuthorizationError, match="User not found"):
        await use_case.execute(bondholder_id=bondholder_id, user_id=user_id)

    mock_bondholder_repo.get_one.assert_awaited_once_with(bondholder_id=bondholder_id)
    mock_user_repo.get_one.assert_awaited_once_with(user_id=user_id)

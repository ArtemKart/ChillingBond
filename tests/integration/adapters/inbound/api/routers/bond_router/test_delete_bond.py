from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

from starlette import status
from starlette.testclient import TestClient


async def test_delete_bondholder_delete_bond(
    client: TestClient,
    mock_current_user: UUID,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    bondholder_entity_mock.user_id = mock_current_user
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.count_by_bond_id.return_value = 0
    mock_bond_repo.delete.return_value = None

    response = client.delete(f"/bonds/{bondholder_entity_mock.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_bondholder_repo.delete.assert_called_once_with(
        bondholder_id=bondholder_entity_mock.id
    )
    mock_bondholder_repo.count_by_bond_id.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )
    mock_bond_repo.delete.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )


async def test_delete_bondholder_keep_bond(
    client: TestClient,
    mock_current_user: UUID,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    bondholder_entity_mock.user_id = mock_current_user
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock
    mock_bondholder_repo.count_by_bond_id.return_value = 1

    response = client.delete(f"/bonds/{bondholder_entity_mock.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_bondholder_repo.delete.assert_called_once_with(
        bondholder_id=bondholder_entity_mock.id
    )
    mock_bondholder_repo.count_by_bond_id.assert_called_once_with(
        bond_id=bondholder_entity_mock.bond_id
    )
    mock_bond_repo.delete.assert_not_called()


async def test_delete_bondholder_bondholder_not_found_idempotent(
    client: TestClient,
    mock_bondholder_repo: AsyncMock,
) -> None:
    mock_bondholder_repo.get_one.return_value = None

    response = client.delete(f"/bonds/{uuid4()}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_bondholder_repo.delete.assert_not_called()


async def test_delete_bondholder_authorization_error(
    client: TestClient,
    mock_bondholder_repo: AsyncMock,
    bondholder_entity_mock: Mock,
    mock_current_user: UUID,
) -> None:
    mock_bondholder_repo.get_one.return_value = bondholder_entity_mock

    response = client.delete(f"/bonds/{uuid4()}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Permission denied"

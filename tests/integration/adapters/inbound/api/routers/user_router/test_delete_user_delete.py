from uuid import uuid4, UUID
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.outbound.database.models import User as UserModel


async def test_delete_user_success(
    client: AsyncClient,
    t_current_user: UUID,
    t_session: AsyncSession,
) -> None:
    r = await client.delete(f"api/users/{t_current_user}")

    assert r.status_code == status.HTTP_204_NO_CONTENT
    assert r.content == b""

    u = await t_session.get(UserModel, t_current_user)
    assert not u


# async def test_delete_user_not_found(client: AsyncClient) -> None:
#     r = await client.delete(f"api/users/{uuid4()}")
#
#     assert r.status_code == status.HTTP_404_NOT_FOUND
#     assert r.json()["detail"] == "User not found"


# async def test_delete_user_invalid_uuid(client: AsyncClient, mock_user_repo: AsyncMock):
#     response = await client.delete("api/users/invalid-uuid")
#
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
#     mock_user_repo.get_one.assert_not_called()
#     mock_user_repo.delete.assert_not_called()
#
#
# async def test_delete_user_calls_in_correct_order(
#     client: AsyncClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
# ):
#     user_id = user_entity_mock.id
#     mock_user_repo.get_one.return_value = user_entity_mock
#     mock_user_repo.delete.return_value = None
#
#     response = await client.delete(f"api/users/{user_id}")
#
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#
#     assert mock_user_repo.get_one.call_count == 1
#     assert mock_user_repo.delete.call_count == 1
#
#     calls = [call[0] for call in mock_user_repo.method_calls]
#     assert calls.index("get_one") < calls.index("delete")

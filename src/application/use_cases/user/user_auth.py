from uuid import UUID

from src.application.dto.user import UserDTO
from src.application.use_cases.user.user_base import UserBaseUseCase
from src.domain.exceptions import InvalidTokenError, NotFoundError
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.token_handler import TokenHandler


class UserAuthUseCase(UserBaseUseCase):
    def __init__(self, user_repo: UserRepository, token_handler: TokenHandler) -> None:
        self.user_repo = user_repo
        self.token_handler = token_handler

    async def execute(self, token: str) -> UserDTO:
        user_id_str: str = await self.token_handler.read_token(subject=token)
        if user_id_str is None:
            raise InvalidTokenError("Invalid token")

        user_id: UUID = UUID(user_id_str)
        user = await self.user_repo.get_one(user_id=user_id)
        if user is None:
            raise NotFoundError("User not found")
        return await self.to_dto(user)

from uuid import UUID

from jwt import PyJWTError

from src.application.dto.user import UserDTO
from src.application.use_cases.user.user_base import UserBaseUseCase
from src.domain.exceptions import AuthenticationError, InvalidTokenError
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.token_handler import TokenHandler


class UserAuthUseCase(UserBaseUseCase):
    def __init__(self, user_repo: UserRepository, token_handler: TokenHandler) -> None:
        self.user_repo = user_repo
        self.token_handler = token_handler

    async def execute(self, token: str) -> UserDTO:
        try:
            user_id_str = self.token_handler.read_token(subject=token)
        except PyJWTError:
            raise InvalidTokenError("Invalid token")
        if not user_id_str:
            raise InvalidTokenError("Token does not contain user information")

        user_id = UUID(user_id_str)
        user = await self.user_repo.get_one(user_id=user_id)
        if user is None:
            raise AuthenticationError("User not found")
        return self.to_dto(user)

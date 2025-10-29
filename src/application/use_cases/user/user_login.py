from src.application.dto.token import TokenDTO
from src.application.use_cases.user.user_base import UserBaseUseCase
from src.domain.exceptions import AuthenticationError
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.ports.services.token_handler import TokenHandler


class UserLoginUseCase(UserBaseUseCase):
    def __init__(
        self,
        user_repo: UserRepository,
        hasher: PasswordHasher,
        token_handler: TokenHandler,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_handler = token_handler

    async def execute(self, form_data) -> TokenDTO:
        user = await self.user_repo.get_by_email(form_data.username)
        if not user or not user.verify_password(
            hasher=self.hasher, plain_password=form_data.password
        ):
            raise AuthenticationError("Incorrect username or password")
        token = self.token_handler.create_token(
            subject=str(user.id),
        )
        return TokenDTO(
            token=token.token,
            type=token.type,
        )

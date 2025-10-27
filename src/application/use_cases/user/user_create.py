from src.application.dto.user import UserCreateDTO, UserDTO
from src.application.use_cases.user.user_base import UserBaseUseCase
from src.domain.exceptions import ValidationError
from src.domain.ports.repositories.user import UserRepository
from src.domain.entities.user import User as UserEntity
from src.domain.ports.services.password_hasher import PasswordHasher


class UserCreateUseCase(UserBaseUseCase):
    def __init__(self, user_repo: UserRepository, hasher: PasswordHasher) -> None:
        self.hasher = hasher
        self.user_repo = user_repo

    async def execute(self, user_dto: UserCreateDTO) -> UserDTO:
        user = await self.user_repo.get_by_email(user_dto.email)
        if user:
            error_msg = "User already exists"
            raise ValidationError(error_msg)

        user = UserEntity.create(
            email=user_dto.email,
            plain_password=user_dto.password,
            hasher=self.hasher,
            name=user_dto.name,
        )
        user_entity = await self.user_repo.write(user)
        return self.to_dto(user_entity)

from src.domain.entities.user import User as UserEntity
from src.application.dto.user import UserDTO


class UserBaseUseCase:
    @staticmethod
    async def to_dto(user: UserEntity) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            name=user.name,
        )

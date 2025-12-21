from src.application.dto.user import UserCreateDTO, UserDTO
from src.application.events.event_publisher import EventPublisher
from src.application.use_cases.user.base import UserBaseUseCase
from src.domain.events.base import DomainEvent
from src.domain.exceptions import ConflictError
from src.domain.ports.repositories.user import UserRepository
from src.domain.entities.user import User as UserEntity
from src.domain.ports.services.password_hasher import PasswordHasher


class UserCreateUseCase(UserBaseUseCase):
    def __init__(
        self,
        user_repo: UserRepository,
        hasher: PasswordHasher,
        event_publisher: EventPublisher,
    ) -> None:
        self.hasher: PasswordHasher = hasher
        self.user_repo: UserRepository = user_repo
        self._event_publisher: EventPublisher = event_publisher

    async def execute(self, user_dto: UserCreateDTO) -> UserDTO:
        user = await self.user_repo.get_by_email(user_dto.email)
        if user:
            error_msg = "User already exists"
            raise ConflictError(error_msg)
        user = UserEntity.create(
            email=user_dto.email,
            plain_password=user_dto.password,
            hasher=self.hasher,
            name=user_dto.name,
        )

        events: list[DomainEvent] = user.collect_events()
        user_entity = await self.user_repo.write(user)
        await self._event_publisher.publish_all(events)

        return self.to_dto(user_entity)

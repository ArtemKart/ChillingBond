from src.application.dto.user import UserCreateDTO, UserDTO
from src.application.events.event_publisher import EventPublisher
from src.application.use_cases.user.user_base import UserBaseUseCase
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
        self.hasher = hasher
        self.user_repo = user_repo
        self._event_publisher = event_publisher

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

        events = user.collect_events()

        user_entity = await self.user_repo.write(user)

        await self._event_publisher.publish_all(events)

        # logger.info(
        #     "User created successfully",
        #     user_id=user_entity.id,
        #     events_published=len(events),
        # )

        return self.to_dto(user_entity)

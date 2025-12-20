from uuid import UUID

from src.application.events.event_publisher import EventPublisher
from src.application.use_cases.bondholder.base import BondHolderBaseUseCase
from src.domain.exceptions import AuthorizationError, NotFoundError
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


class BondHolderDeleteUseCase(BondHolderBaseUseCase):
    def __init__(
        self,
        bondholder_repo: BondHolderRepository,
        event_publisher: EventPublisher,
        user_repo: UserRepository,
        bh_del_service: BondHolderDeletionService,
    ) -> None:
        self.bondholder_repo: BondHolderRepository = bondholder_repo
        self.event_publisher: EventPublisher = event_publisher
        self.user_repo: UserRepository = user_repo
        self.bh_del_service: BondHolderDeletionService = bh_del_service

    async def execute(self, bondholder_id: UUID, user_id: UUID) -> None:
        bondholder = await self.bondholder_repo.get_one(bondholder_id=bondholder_id)
        if not bondholder:
            raise NotFoundError("Bondholder not found")

        if bondholder.user_id != user_id:
            raise AuthorizationError("Permission denied")
        user = await self.user_repo.get_one(user_id=user_id)
        if not user:
            raise AuthorizationError("User not found")

        bondholder.mark_as_deleted(user_email=user.email)
        events = bondholder.collect_events()

        await self.bh_del_service.delete_with_cleanup(
            bondholder_id=bondholder.id, bond_id=bondholder.bond_id
        )
        await self.event_publisher.publish_all(events)

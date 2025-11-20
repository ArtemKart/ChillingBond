from uuid import UUID

from src.application.events.event_publisher import EventPublisher
from src.application.use_cases.bondholder.bondholder_base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, AuthorizationError
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
        self._bondholder_repo = bondholder_repo
        self._event_publisher = event_publisher
        self._user_repo = user_repo
        self._bh_del_service = bh_del_service

    async def execute(self, bondholder_id: UUID, user_id: UUID) -> None:
        bondholder = await self._bondholder_repo.get_one(bondholder_id=bondholder_id)
        if not bondholder:
            raise NotFoundError("Bondholder not found")

        if bondholder.user_id != user_id:
            raise AuthorizationError("Permission denied")
        user = await self._user_repo.get_one(user_id=user_id)

        bondholder.mark_as_deleted(user_email=user.email)
        events = bondholder.collect_events()

        await self._bh_del_service.delete_with_cleanup(
            bondholder_id=bondholder.id, bond_id=bondholder.bond_id
        )
        await self._event_publisher.publish_all(events)

from uuid import UUID

from src.domain.exceptions import NotFoundError, AuthorizationError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository


class BondHolderDeletionService:
    """Service handling bondholder deletion with orphaned bond cleanup."""

    def __init__(
        self,
        bondholder_repo: BondHolderRepository,
        bond_repo: BondRepository,
    ):
        self._bondholder_repo = bondholder_repo
        self._bond_repo = bond_repo

    async def delete_with_cleanup(self, bondholder_id: UUID, user_id: UUID) -> None:
        """
        Delete bondholder and cleanup orphaned bond if needed.

        Returns:
            None

        Raises:
            NotFoundError if bondholder is not found.
            AuthorizationError if user is not authorized.
        """
        bondholder = await self._bondholder_repo.get_one(bondholder_id=bondholder_id)
        if not bondholder:
            raise NotFoundError("Bondholder not found")

        if bondholder.user_id != user_id:
            raise AuthorizationError("Permission denied")

        bond_id = bondholder.bond_id

        await self._bondholder_repo.delete(bondholder_id=bondholder.id)
        remaining_holders = await self._bondholder_repo.count_by_bond_id(
            bond_id=bond_id
        )

        if remaining_holders == 0:
            await self._bond_repo.delete(bond_id=bond_id)

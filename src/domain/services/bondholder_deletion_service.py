from uuid import UUID

from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository


class BondHolderDeletionService:
    """Service handling bondholder deletion with orphaned bond cleanup."""

    def __init__(
        self,
        bondholder_repo: BondHolderRepository,
        bond_repo: BondRepository,
    ):
        self._bondholder_repo: BondHolderRepository = bondholder_repo
        self._bond_repo: BondRepository = bond_repo

    async def delete_with_cleanup(self, bondholder_id: UUID, bond_id: UUID) -> None:
        """
        Delete bondholder and cleanup orphaned bond if needed.

        Returns:
            None

        Raises:
            NotFoundError if bondholder is not found.
            AuthorizationError if user is not authorized.
        """

        await self._bondholder_repo.delete(bondholder_id=bondholder_id)
        remaining_holders = await self._bondholder_repo.count_by_bond_id(
            bond_id=bond_id
        )

        if remaining_holders == 0:
            await self._bond_repo.delete(bond_id=bond_id)

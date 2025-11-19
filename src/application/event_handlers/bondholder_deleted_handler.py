from src.domain.events.bondholder_events import BondHolderDeleted
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository


class BondHolderDeletedHandler:
    """Handles cleanup of orphaned bonds when bondholder is deleted."""

    def __init__(
        self,
        bondholder_repo: BondHolderRepository,
        bond_repo: BondRepository,
    ) -> None:
        self._bondholder_repo = bondholder_repo
        self._bond_repo = bond_repo

    async def handle(self, event: BondHolderDeleted) -> None:
        """Delete bond if no other bondholders reference it."""
        remaining_holders = await self._bondholder_repo.count_by_bond_id(
            bond_id=event.bond_id
        )

        if remaining_holders == 0:
            await self._bond_repo.delete(bond_id=event.bond_id)

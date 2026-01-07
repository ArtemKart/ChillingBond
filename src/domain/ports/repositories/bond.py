from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.bond import Bond


class BondRepository(ABC):
    """Abstract repository for managing bond entities.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for Bond entities
    in various data stores.
    """

    @abstractmethod
    async def get_one(self, bond_id: UUID) -> Bond | None:
        """Retrieves a bond by its identifier.

        Args:
            bond_id: The unique identifier of the bond.

        Returns:
            A Bond object if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_series(self, series: str) -> Bond | None:
        """Retrieves a bond by series.
        Args:
            series: The unique series identifier.

        Returns:
            A Bond object if found, None otherwise
        """
        pass

    @abstractmethod
    async def write(self, bond: Bond) -> Bond:
        """Creates a new bond in the repository.

        Args:
            bond: The Bond object to persist.

        Returns:
            The persisted Bond object if created, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, bond: Bond) -> Bond:
        """Updates an existing bond in the repository.

        Args:
            bond: The Bond object with updated data.

        Returns:
            The updated Bond object if updated, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, bond_id: UUID) -> Bond | None:
        """Deletes a bond from the repository.

        Args:
            bond_id: The unique identifier of the bondholder to delete.

        Returns:
            The deleted Bond object if deleted, None otherwise.
        """
        pass

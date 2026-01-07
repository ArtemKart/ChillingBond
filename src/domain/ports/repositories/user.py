from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository for managing user entities.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for User entities
    in various data stores.
    """

    @abstractmethod
    async def get_user_or_none(self, user_id: UUID) -> User | None:
        """
        Checks if a user with the given UUID exists.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            A User object if found, None otherwise.
        """

    @abstractmethod
    async def get_user_or_none_by_email(self, email: str) -> User | None:
        """
        Checks if a user with the given email exists.

        Args:
            email: User email address.

        Returns:
            A User object if found, None otherwise.
        """

    @abstractmethod
    async def write(self, user: User) -> User | None:
        """Creates a new user in the repository.

        Args:
            user: The User object to persist.

        Returns:
            The persisted User object.
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> User | None:
        """Deletes a user from the repository.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            The deleted User object if found, None otherwise.
        """
        pass

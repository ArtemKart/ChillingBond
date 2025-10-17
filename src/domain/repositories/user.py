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
    async def get_one(self, user_id: UUID) -> User | None:
        """Retrieves a user by its identifier.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            A User object if found, None otherwise.
        """

        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by its email.

        Args:
            email: User email address.

        Returns:
            A User object if found, None otherwise.
        """
        pass

    @abstractmethod
    async def write(self, user: User) -> User:
        """Creates a new user in the repository.

        Args:
            user: The User object to persist.

        Returns:
            The persisted User object.
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Updates an existing user in the repository.

        Args:
            user: The User object with updated data.

        Returns:
            The updated User object.
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Deletes a user from the repository.

        Args:
            user_id: The unique identifier of the user to delete.
        """
        pass

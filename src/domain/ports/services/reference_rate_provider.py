from abc import abstractmethod, ABC
from datetime import date
from decimal import Decimal


class ReferenceRateProvider(ABC):
    """
    Interface for fetching reference rate data from external sources.

    This is a Port in Hexagonal Architecture.
    Implementation can be NBP, ECB, Fed, or any other source.
    """

    @abstractmethod
    async def get_current_rate(self) -> tuple[Decimal, date]:
        """
        Fetch current reference rate.

        Returns:
            Tuple of (rate_value, effective_date)

        Raises:
            ExternalServiceError: If data cannot be fetched or parsed
        """
        pass

import logging
from decimal import Decimal
from datetime import date

from src.domain.ports.services.reference_rate_provider import ReferenceRateProvider
from .fetcher import NBPXMLFetcher
from .parser import NBPXMLParser

logger = logging.getLogger(__name__)


class NBPDataProvider(ReferenceRateProvider):
    """
    NBP implementation of ReferenceRateProvider.

    This is the main adapter class that:
    1. Uses NBPXMLFetcher to download XML data
    2. Uses NBPXMLParser to parse XML
    3. Implements ReferenceRateProvider port
    """

    def __init__(self, fetcher: NBPXMLFetcher, parser: NBPXMLParser):
        """
        Initialize NBP data provider.

        Args:
            fetcher: NBP XML fetcher instance
            parser: NBP XML parser instance
        """
        self._fetcher = fetcher
        self._parser = parser

    async def get_current_rate(self) -> tuple[Decimal, date]:
        """
        Fetch current NBP reference rate.

        Workflow:
        1. Fetch XML from NBP
        2. Parse XML to extract rate data
        3. Convert to domain types

        Returns:
            Tuple of (rate_value, effective_date)

        Raises:
            ExternalServiceError: If data cannot be fetched or parsed
        """
        logger.info("Fetching current NBP reference rate")

        xml_content = await self._fetcher.fetch()

        scraped_data = self._parser.parse(xml_content)

        rate_value, effective_date = self._parser.convert_to_domain(scraped_data)

        logger.info(
            f"Successfully obtained NBP rate: {rate_value}% "
            f"effective from {effective_date}"
        )

        return rate_value, effective_date

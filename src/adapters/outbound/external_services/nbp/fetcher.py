import httpx
import logging
from typing import Optional

from src.adapters.outbound.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class NBPXMLFetcher:
    """
    HTTP client for fetching NBP XML data feed.

    Handles:
    - HTTP requests to NBP
    - Network error handling
    - Retry logic with exponential backoff
    """

    NBP_XML_URL = "https://static.nbp.pl/dane/stopy/stopy_procentowe.xml"

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize NBP XML fetcher.

        Args:
            timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Lazy initialization of HTTP client.

        Returns:
            Configured async HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={"User-Agent": "ChillingBond/1.0 (Bond Portfolio Manager)"},
                follow_redirects=True,
            )
        return self._client

    async def fetch(self) -> str:
        """
        Fetch NBP XML data.

        Implements retry logic with exponential backoff.

        Returns:
            XML content as string

        Raises:
            ExternalServiceError: If fetching fails after all retries
        """
        import asyncio

        client = await self._get_client()

        for attempt in range(self._max_retries):
            try:
                logger.info(
                    f"Fetching NBP XML (attempt {attempt + 1}/{self._max_retries}): "
                    f"{self.NBP_XML_URL}"
                )

                response = await client.get(self.NBP_XML_URL)
                response.raise_for_status()

                xml_content = response.text

                logger.info(f"Successfully fetched NBP XML ({len(xml_content)} bytes)")

                return xml_content

            except httpx.HTTPError as e:
                logger.warning(
                    f"HTTP error on attempt {attempt + 1}/{self._max_retries}: {e}"
                )

                if attempt == self._max_retries - 1:
                    raise ExternalServiceError(
                        f"Failed to fetch NBP XML after {self._max_retries} attempts: {e}"
                    ) from e

                backoff_time = 2**attempt
                logger.info(f"Retrying in {backoff_time} seconds...")
                await asyncio.sleep(backoff_time)

            except Exception as e:
                logger.error(
                    f"Unexpected error while fetching NBP XML: {e}", exc_info=True
                )
                raise ExternalServiceError(f"Failed to fetch NBP XML: {e}") from e

        raise ExternalServiceError("Failed to fetch NBP XML: max retries exceeded")

    async def close(self):
        """Close HTTP client and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

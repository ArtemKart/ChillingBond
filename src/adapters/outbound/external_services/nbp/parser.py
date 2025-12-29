from decimal import Decimal
from datetime import datetime, date

# bandit false-positive: Use of xml.etree.ElementTree module
import xml.etree.ElementTree as ET  # nosec B405
import logging

from .models import NBPScrapedData
from src.adapters.outbound.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class NBPXMLParser:
    """
    Parser for NBP XML data feed.

    Parses XML from: https://static.nbp.pl/dane/stopy/stopy_procentowe.xml
    Extracts reference rate (stopa referencyjna) and effective date.
    """

    @staticmethod
    def parse(xml_content: str) -> NBPScrapedData:
        """
        Parse NBP XML and extract reference rate data.

        Args:
            xml_content: XML content as string

        Returns:
            NBPScrapedData with extracted data

        Raises:
            ExternalServiceError: If parsing fails
        """
        try:
            # bandit false-positive: Use of xml.etree.ElementTree module
            root = ET.fromstring(xml_content)  # nosec B314
            ref_position = root.find(".//pozycja[@id='ref']")

            if ref_position is None:
                raise ValueError("Reference rate position not found in XML")

            rate_value = ref_position.get("oprocentowanie")
            effective_date = ref_position.get("obowiazuje_od")

            if not rate_value or not effective_date:
                raise ValueError("Missing rate or date attributes in XML")

            logger.info(
                f"Successfully parsed NBP XML: rate={rate_value}, date={effective_date}"
            )

            return NBPScrapedData(
                rate_value=rate_value, effective_date_str=effective_date
            )

        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}", exc_info=True)
            raise ExternalServiceError(f"Invalid XML format: {e}") from e
        except Exception as e:
            logger.error(f"Failed to extract data from XML: {e}", exc_info=True)
            raise ExternalServiceError(f"Failed to parse NBP XML: {e}") from e

    @staticmethod
    def convert_to_domain(scraped: NBPScrapedData) -> tuple[Decimal, date]:
        """
        Convert scraped data to domain types.

        Transforms string data into proper domain types (Decimal, date).

        Args:
            scraped: NBPScrapedData with raw string data

        Returns:
            Tuple of (rate_value, effective_date) as domain types

        Raises:
            ValueError: If conversion fails
        """
        try:
            rate_str = scraped.rate_value.replace(",", ".")
            rate_value = Decimal(rate_str)
        except Exception as e:
            raise ValueError(f"Invalid rate value: {scraped.rate_value}") from e

        try:
            effective_date = datetime.strptime(
                scraped.effective_date_str, "%Y-%m-%d"
            ).date()
        except Exception as e:
            raise ValueError(f"Invalid date format: {scraped.effective_date_str}") from e

        return rate_value, effective_date

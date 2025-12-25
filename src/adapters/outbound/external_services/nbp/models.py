from dataclasses import dataclass


@dataclass
class NBPScrapedData:
    """
    Data structure to hold scraped NBP reference rate data.

    This is an intermediate model between fetcher/parser and domain layer.
    Contains raw string data before conversion to domain types.
    """

    rate_value: str
    effective_date_str: str

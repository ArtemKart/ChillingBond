import logging
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest
from pytest import LogCaptureFixture

from src.adapters.outbound.exceptions import ExternalServiceError
from src.adapters.outbound.external_services.nbp.fetcher import NBPXMLFetcher
from src.adapters.outbound.external_services.nbp.models import NBPScrapedData
from src.adapters.outbound.external_services.nbp.nbp_data_provider import (
    NBPDataProvider,
)
from src.adapters.outbound.external_services.nbp.parser import NBPXMLParser


@pytest.fixture
def mock_fetcher() -> AsyncMock:
    return AsyncMock(spec=NBPXMLFetcher)


@pytest.fixture
def mock_parser() -> Mock:
    parser = Mock(spec=NBPXMLParser)
    parser.parse = Mock()
    parser.convert_to_domain = Mock()
    return parser


@pytest.fixture
def provider(mock_fetcher: AsyncMock, mock_parser: Mock) -> NBPDataProvider:
    return NBPDataProvider(fetcher=mock_fetcher, parser=mock_parser)


@pytest.fixture
def sample_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""


@pytest.fixture
def sample_scraped_data() -> NBPScrapedData:
    return NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")


def test_init_with_dependencies(mock_fetcher: AsyncMock, mock_parser: Mock) -> None:
    provider = NBPDataProvider(fetcher=mock_fetcher, parser=mock_parser)

    assert provider._fetcher is mock_fetcher
    assert provider._parser is mock_parser


def test_init_stores_references() -> None:
    fetcher = AsyncMock(spec=NBPXMLFetcher)
    parser = Mock(spec=NBPXMLParser)

    provider = NBPDataProvider(fetcher=fetcher, parser=parser)

    assert provider._fetcher is fetcher
    assert provider._parser is parser


async def test_get_current_rate_success(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
    caplog: LogCaptureFixture,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    with caplog.at_level(logging.INFO):
        rate, effective_date = await provider.get_current_rate()

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)

    mock_fetcher.fetch.assert_called_once()
    mock_parser.parse.assert_called_once_with(sample_xml)
    mock_parser.convert_to_domain.assert_called_once_with(sample_scraped_data)

    assert "Fetching current NBP reference rate" in caplog.text
    assert "Successfully obtained NBP rate: 5.75%" in caplog.text
    assert "effective from 2024-01-15" in caplog.text


async def test_get_current_rate_calls_fetcher(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    await provider.get_current_rate()

    mock_fetcher.fetch.assert_called_once()


async def test_get_current_rate_calls_parser_parse(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    await provider.get_current_rate()

    mock_parser.parse.assert_called_once_with(sample_xml)


async def test_get_current_rate_calls_parser_convert(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    await provider.get_current_rate()

    mock_parser.convert_to_domain.assert_called_once_with(sample_scraped_data)


async def test_get_current_rate_fetcher_error_propagates(
    provider: NBPDataProvider, mock_fetcher: AsyncMock, mock_parser: Mock
) -> None:
    mock_fetcher.fetch.side_effect = ExternalServiceError("Network error")

    with pytest.raises(ExternalServiceError) as exc_info:
        await provider.get_current_rate()

    assert "Network error" in str(exc_info.value)
    mock_parser.parse.assert_not_called()


async def test_get_current_rate_parser_parse_error_propagates(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.side_effect = ExternalServiceError("Invalid XML")

    with pytest.raises(ExternalServiceError) as exc_info:
        await provider.get_current_rate()

    assert "Invalid XML" in str(exc_info.value)
    mock_parser.convert_to_domain.assert_not_called()


async def test_get_current_rate_parser_convert_error_propagates(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.side_effect = ValueError("Invalid rate format")

    with pytest.raises(ValueError) as exc_info:
        await provider.get_current_rate()

    assert "Invalid rate format" in str(exc_info.value)


async def test_get_current_rate_with_different_rates(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
) -> None:
    test_cases = [
        (Decimal("0.50"), date(2024, 1, 1)),
        (Decimal("10.00"), date(2024, 6, 15)),
        (Decimal("7.25"), date(2024, 12, 31)),
    ]

    for expected_rate, expected_date in test_cases:
        scraped = NBPScrapedData(
            rate_value=str(expected_rate), effective_date_str=str(expected_date)
        )

        mock_fetcher.fetch.return_value = sample_xml
        mock_parser.parse.return_value = scraped
        mock_parser.convert_to_domain.return_value = (
            expected_rate,
            expected_date,
        )

        rate, effective_date = await provider.get_current_rate()

        assert rate == expected_rate
        assert effective_date == expected_date


async def test_get_current_rate_returns_tuple(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    result = await provider.get_current_rate()

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], Decimal)
    assert isinstance(result[1], date)


async def test_get_current_rate_logs_start(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
    caplog: LogCaptureFixture,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    with caplog.at_level(logging.INFO):
        await provider.get_current_rate()

    assert "Fetching current NBP reference rate" in caplog.text


async def test_get_current_rate_logs_success(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
    caplog: LogCaptureFixture,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    with caplog.at_level(logging.INFO):
        await provider.get_current_rate()

    assert "Successfully obtained NBP rate" in caplog.text
    assert "5.75%" in caplog.text
    assert "2024-01-15" in caplog.text


async def test_full_workflow_with_real_components() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5,75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""

    parser = NBPXMLParser()
    fetcher = AsyncMock(spec=NBPXMLFetcher)
    fetcher.fetch.return_value = xml

    provider = NBPDataProvider(fetcher=fetcher, parser=parser)

    rate, effective_date = await provider.get_current_rate()

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)
    fetcher.fetch.assert_called_once()


async def test_workflow_handles_parsing_errors_gracefully() -> None:
    invalid_xml = "This is not valid XML"

    parser = NBPXMLParser()
    fetcher = AsyncMock(spec=NBPXMLFetcher)
    fetcher.fetch.return_value = invalid_xml

    provider = NBPDataProvider(fetcher=fetcher, parser=parser)

    with pytest.raises(ExternalServiceError):
        await provider.get_current_rate()


async def test_workflow_handles_conversion_errors() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="invalid_rate" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""

    parser = NBPXMLParser()
    fetcher = AsyncMock(spec=NBPXMLFetcher)
    fetcher.fetch.return_value = xml

    provider = NBPDataProvider(fetcher=fetcher, parser=parser)

    with pytest.raises(ValueError):
        await provider.get_current_rate()


async def test_multiple_calls_work_correctly(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
) -> None:
    test_data = [
        (
            NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15"),
            Decimal("5.75"),
            date(2024, 1, 15),
        ),
        (
            NBPScrapedData(rate_value="6.00", effective_date_str="2024-02-01"),
            Decimal("6.00"),
            date(2024, 2, 1),
        ),
        (
            NBPScrapedData(rate_value="5.50", effective_date_str="2024-03-01"),
            Decimal("5.50"),
            date(2024, 3, 1),
        ),
    ]

    for scraped, expected_rate, expected_date in test_data:
        mock_fetcher.fetch.return_value = sample_xml
        mock_parser.parse.return_value = scraped
        mock_parser.convert_to_domain.return_value = (
            expected_rate,
            expected_date,
        )

        rate, effective_date = await provider.get_current_rate()

        assert rate == expected_rate
        assert effective_date == expected_date


async def test_implements_reference_rate_provider_interface(
    provider: NBPDataProvider,
) -> None:
    from src.domain.ports.services.reference_rate_provider import (
        ReferenceRateProvider,
    )

    assert isinstance(provider, ReferenceRateProvider)

    assert hasattr(provider, "get_current_rate")
    assert callable(provider.get_current_rate)


async def test_get_current_rate_signature_matches_interface(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.return_value = (
        Decimal("5.75"),
        date(2024, 1, 15),
    )

    result = await provider.get_current_rate()

    assert isinstance(result, tuple)
    assert isinstance(result[0], Decimal)
    assert isinstance(result[1], date)


async def test_handles_fetcher_timeout_error(
    provider: NBPDataProvider, mock_fetcher: AsyncMock
) -> None:
    mock_fetcher.fetch.side_effect = ExternalServiceError("Request timeout")

    with pytest.raises(ExternalServiceError) as exc_info:
        await provider.get_current_rate()

    assert "timeout" in str(exc_info.value).lower()


async def test_handles_fetcher_network_error(
    provider: NBPDataProvider, mock_fetcher: AsyncMock
) -> None:
    mock_fetcher.fetch.side_effect = ExternalServiceError("Connection refused")

    with pytest.raises(ExternalServiceError) as exc_info:
        await provider.get_current_rate()

    assert "Connection refused" in str(exc_info.value)


async def test_handles_parser_xml_error(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.side_effect = ExternalServiceError("Invalid XML format")

    with pytest.raises(ExternalServiceError) as exc_info:
        await provider.get_current_rate()

    assert "Invalid XML format" in str(exc_info.value)


async def test_handles_parser_conversion_error(
    provider: NBPDataProvider,
    mock_fetcher: AsyncMock,
    mock_parser: Mock,
    sample_xml: str,
    sample_scraped_data: NBPScrapedData,
) -> None:
    mock_fetcher.fetch.return_value = sample_xml
    mock_parser.parse.return_value = sample_scraped_data
    mock_parser.convert_to_domain.side_effect = ValueError("Invalid rate value")

    with pytest.raises(ValueError) as exc_info:
        await provider.get_current_rate()

    assert "Invalid rate value" in str(exc_info.value)


async def test_does_not_catch_unexpected_exceptions(
    provider: NBPDataProvider, mock_fetcher: AsyncMock
) -> None:
    mock_fetcher.fetch.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError) as exc_info:
        await provider.get_current_rate()

    assert "Unexpected error" in str(exc_info.value)

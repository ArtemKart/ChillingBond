import logging
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from pytest import LogCaptureFixture

from src.adapters.outbound.exceptions import ExternalServiceError
from src.adapters.outbound.external_services.nbp.fetcher import NBPXMLFetcher


@pytest.fixture
def fetcher() -> NBPXMLFetcher:
    return NBPXMLFetcher(timeout=30, max_retries=3)


@pytest.fixture
def fetcher_short_timeout() -> NBPXMLFetcher:
    return NBPXMLFetcher(timeout=5, max_retries=2)


@pytest.fixture
def mock_xml_response() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-01"/>
</stopy_procentowe>"""


async def test_get_client_creates_client(fetcher: NBPXMLFetcher) -> None:
    client = await fetcher._get_client()

    assert client is not None
    assert isinstance(client, httpx.AsyncClient)
    assert fetcher._client is client


async def test_get_client_returns_same_instance(fetcher: NBPXMLFetcher) -> None:
    client1 = await fetcher._get_client()
    client2 = await fetcher._get_client()

    assert client1 is client2


async def test_get_client_configures_timeout(
    fetcher_short_timeout: NBPXMLFetcher,
) -> None:
    client = await fetcher_short_timeout._get_client()

    assert client.timeout.read == 5


async def test_get_client_configures_user_agent(fetcher: NBPXMLFetcher) -> None:
    client = await fetcher._get_client()

    assert "User-Agent" in client.headers
    assert "ChillingBond" in client.headers["User-Agent"]


async def test_get_client_follows_redirects(fetcher: NBPXMLFetcher) -> None:
    client = await fetcher._get_client()

    assert client.follow_redirects is True


async def test_fetch_success(
    fetcher: NBPXMLFetcher, mock_xml_response: str, caplog: LogCaptureFixture
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    fetcher._client = mock_client

    with caplog.at_level(logging.INFO):
        result = await fetcher.fetch()

    assert result == mock_xml_response
    assert "Successfully fetched NBP XML" in caplog.text
    assert f"({len(mock_xml_response)} bytes)" in caplog.text

    mock_client.get.assert_called_once_with(NBPXMLFetcher.NBP_XML_URL)


async def test_fetch_creates_client_if_not_exists(
    fetcher: NBPXMLFetcher, mock_xml_response: str
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    with patch.object(httpx, "AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        result = await fetcher.fetch()

    assert result == mock_xml_response
    assert fetcher._client is not None


async def test_fetch_http_error_with_retry(
    fetcher: NBPXMLFetcher, mock_xml_response: str, caplog: LogCaptureFixture
) -> None:
    mock_response_success = Mock()
    mock_response_success.text = mock_xml_response
    mock_response_success.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=[
            httpx.HTTPStatusError("404", request=Mock(), response=Mock()),
            mock_response_success,
        ]
    )

    fetcher._client = mock_client

    with caplog.at_level(logging.INFO):
        result = await fetcher.fetch()

    assert result == mock_xml_response
    assert mock_client.get.call_count == 2
    assert "HTTP error on attempt 1/3" in caplog.text
    assert "Retrying in 1 seconds" in caplog.text


async def test_fetch_fails_after_max_retries(
    fetcher_short_timeout: NBPXMLFetcher, caplog: LogCaptureFixture
) -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError("500", request=Mock(), response=Mock())
    )

    fetcher_short_timeout._client = mock_client

    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.WARNING):
            await fetcher_short_timeout.fetch()

    assert "Failed to fetch NBP XML after 2 attempts" in str(exc_info.value)
    assert mock_client.get.call_count == 2


async def test_fetch_timeout_error(fetcher: NBPXMLFetcher) -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))

    fetcher._client = mock_client

    with pytest.raises(ExternalServiceError) as exc_info:
        await fetcher.fetch()

    assert "Failed to fetch NBP XML" in str(exc_info.value)


async def test_fetch_network_error(fetcher: NBPXMLFetcher) -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.NetworkError("Connection refused"))

    fetcher._client = mock_client

    with pytest.raises(ExternalServiceError) as exc_info:
        await fetcher.fetch()

    assert "Failed to fetch NBP XML" in str(exc_info.value)


async def test_fetch_unexpected_exception(
    fetcher: NBPXMLFetcher, caplog: LogCaptureFixture
) -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RuntimeError("Unexpected error"))

    fetcher._client = mock_client

    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.ERROR):
            await fetcher.fetch()

    assert "Failed to fetch NBP XML" in str(exc_info.value)
    assert "Unexpected error while fetching NBP XML" in caplog.text


async def test_fetch_exponential_backoff(
    fetcher: NBPXMLFetcher, mock_xml_response: str
) -> None:
    mock_response_success = Mock()
    mock_response_success.text = mock_xml_response
    mock_response_success.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=[
            httpx.HTTPStatusError("503", request=Mock(), response=Mock()),
            httpx.HTTPStatusError("503", request=Mock(), response=Mock()),
            mock_response_success,
        ]
    )

    fetcher._client = mock_client

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await fetcher.fetch()

    assert result == mock_xml_response

    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)


async def test_fetch_logs_attempts(
    fetcher: NBPXMLFetcher, mock_xml_response: str, caplog: LogCaptureFixture
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    fetcher._client = mock_client

    with caplog.at_level(logging.INFO):
        await fetcher.fetch()

    assert "Fetching NBP XML (attempt 1/3)" in caplog.text
    assert NBPXMLFetcher.NBP_XML_URL in caplog.text


async def test_close_closes_client(fetcher: NBPXMLFetcher) -> None:
    client = await fetcher._get_client()

    with patch.object(client, "aclose", new_callable=AsyncMock) as mock_close:
        await fetcher.close()
        mock_close.assert_called_once()

    assert fetcher._client is None


async def test_close_when_no_client(fetcher: NBPXMLFetcher) -> None:
    assert fetcher._client is None

    await fetcher.close()

    assert fetcher._client is None


async def test_close_sets_client_to_none(fetcher: NBPXMLFetcher) -> None:
    await fetcher._get_client()
    assert fetcher._client is not None

    await fetcher.close()

    assert fetcher._client is None


async def test_fetch_and_close_workflow(
    fetcher: NBPXMLFetcher, mock_xml_response: str
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    with patch.object(httpx, "AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_client_instance

        result = await fetcher.fetch()
        assert result == mock_xml_response

        await fetcher.close()
        mock_client_instance.aclose.assert_called_once()


async def test_multiple_fetches_use_same_client(
    fetcher: NBPXMLFetcher, mock_xml_response: str
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    fetcher._client = mock_client

    await fetcher.fetch()
    await fetcher.fetch()
    await fetcher.fetch()

    assert mock_client.get.call_count == 3


async def test_fetch_after_close_creates_new_client(
    fetcher: NBPXMLFetcher, mock_xml_response: str
) -> None:
    mock_response = Mock()
    mock_response.text = mock_xml_response
    mock_response.raise_for_status = Mock()

    with patch.object(httpx, "AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_client_instance

        await fetcher.fetch()
        _ = fetcher._client

        await fetcher.close()
        assert fetcher._client is None

        await fetcher.fetch()
        assert fetcher._client is not None
        assert mock_client_class.call_count == 2


def test_nbp_xml_url_is_correct() -> None:
    expected_url = "https://static.nbp.pl/dane/stopy/stopy_procentowe.xml"
    assert NBPXMLFetcher.NBP_XML_URL == expected_url

import logging
from datetime import date
from decimal import Decimal

import pytest
from pytest import LogCaptureFixture

from src.adapters.outbound.exceptions import ExternalServiceError
from src.adapters.outbound.external_services.nbp.models import NBPScrapedData
from src.adapters.outbound.external_services.nbp.parser import NBPXMLParser


@pytest.fixture
def valid_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""


@pytest.fixture
def valid_xml_with_comma() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5,75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""


@pytest.fixture
def xml_missing_rate() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""


@pytest.fixture
def xml_missing_date() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75"/>
</stopy_procentowe>"""


@pytest.fixture
def xml_missing_position() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="other" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""


@pytest.fixture
def parser() -> NBPXMLParser:
    return NBPXMLParser()


def test_parse_valid_xml(
    parser: NBPXMLParser, valid_xml: str, caplog: LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        result = parser.parse(valid_xml)

    assert isinstance(result, NBPScrapedData)
    assert result.rate_value == "5.75"
    assert result.effective_date_str == "2024-01-15"

    assert "Successfully parsed NBP XML" in caplog.text
    assert "rate=5.75" in caplog.text
    assert "date=2024-01-15" in caplog.text


def test_parse_valid_xml_with_comma(
    parser: NBPXMLParser, valid_xml_with_comma: str
) -> None:
    result = parser.parse(valid_xml_with_comma)

    assert result.rate_value == "5,75"
    assert result.effective_date_str == "2024-01-15"


def test_parse_with_different_rate_values(parser: NBPXMLParser) -> None:
    test_cases = [
        ("0.50", "2024-01-01"),
        ("10.00", "2024-02-01"),
        ("7,25", "2024-03-01"),
        ("15.5", "2024-04-01"),
    ]

    for rate, date_str in test_cases:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="{rate}" obowiazuje_od="{date_str}"/>
</stopy_procentowe>"""

        result = parser.parse(xml)
        assert result.rate_value == rate
        assert result.effective_date_str == date_str


def test_parse_invalid_xml(parser: NBPXMLParser, caplog: LogCaptureFixture) -> None:
    invalid_xml = "This is not XML"

    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.ERROR):
            parser.parse(invalid_xml)

    assert "Invalid XML format" in str(exc_info.value)
    assert "Failed to parse XML" in caplog.text


def test_parse_malformed_xml(parser: NBPXMLParser) -> None:
    malformed_xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"
</stopy_procentowe>"""

    with pytest.raises(ExternalServiceError) as exc_info:
        parser.parse(malformed_xml)

    assert "Invalid XML format" in str(exc_info.value)


def test_parse_missing_reference_position(
    parser: NBPXMLParser, xml_missing_position: str, caplog: LogCaptureFixture
) -> None:
    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.ERROR):
            parser.parse(xml_missing_position)

    assert "Failed to parse NBP XML" in str(exc_info.value)
    assert "Reference rate position not found" in str(exc_info.value)


def test_parse_missing_rate_attribute(
    parser: NBPXMLParser, xml_missing_rate: str, caplog: LogCaptureFixture
) -> None:
    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.ERROR):
            parser.parse(xml_missing_rate)

    assert "Failed to parse NBP XML" in str(exc_info.value)
    assert "Missing rate or date attributes" in str(exc_info.value)


def test_parse_missing_date_attribute(
    parser: NBPXMLParser, xml_missing_date: str, caplog: LogCaptureFixture
) -> None:
    with pytest.raises(ExternalServiceError) as exc_info:
        with caplog.at_level(logging.ERROR):
            parser.parse(xml_missing_date)

    assert "Failed to parse NBP XML" in str(exc_info.value)
    assert "Missing rate or date attributes" in str(exc_info.value)


def test_parse_empty_xml(parser: NBPXMLParser) -> None:
    empty_xml = ""

    with pytest.raises(ExternalServiceError):
        parser.parse(empty_xml)


def test_parse_xml_with_empty_attributes(parser: NBPXMLParser) -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="" obowiazuje_od=""/>
</stopy_procentowe>"""

    with pytest.raises(ExternalServiceError) as exc_info:
        parser.parse(xml)

    assert "Missing rate or date attributes" in str(exc_info.value)


def test_parse_xml_with_nested_structure(parser: NBPXMLParser) -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <stopy_procentowe>
        <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
    </stopy_procentowe>
</root>"""

    result = parser.parse(xml)

    assert result.rate_value == "5.75"
    assert result.effective_date_str == "2024-01-15"


def test_parse_xml_with_multiple_positions(parser: NBPXMLParser) -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="other" oprocentowanie="1.00" obowiazuje_od="2024-01-01"/>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
    <pozycja id="another" oprocentowanie="2.00" obowiazuje_od="2024-01-20"/>
</stopy_procentowe>"""

    result = parser.parse(xml)

    assert result.rate_value == "5.75"
    assert result.effective_date_str == "2024-01-15"


def test_parse_xml_with_special_characters_in_data(parser: NBPXMLParser) -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15" note="Test &amp; data"/>
</stopy_procentowe>"""

    result = parser.parse(xml)

    assert result.rate_value == "5.75"
    assert result.effective_date_str == "2024-01-15"


def test_convert_valid_data_with_dot(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    rate, effective_date = parser.convert_to_domain(scraped)

    assert isinstance(rate, Decimal)
    assert rate == Decimal("5.75")
    assert isinstance(effective_date, date)
    assert effective_date == date(2024, 1, 15)


def test_convert_valid_data_with_comma(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5,75", effective_date_str="2024-01-15")

    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)


def test_convert_various_rate_formats(parser: NBPXMLParser) -> None:
    test_cases = [
        ("0.50", Decimal("0.50")),
        ("10.00", Decimal("10.00")),
        ("7,25", Decimal("7.25")),
        ("15", Decimal("15")),
        ("0,1", Decimal("0.1")),
    ]

    for rate_str, expected_decimal in test_cases:
        scraped = NBPScrapedData(rate_value=rate_str, effective_date_str="2024-01-01")
        rate, _ = parser.convert_to_domain(scraped)
        assert rate == expected_decimal


def test_convert_various_date_formats(parser: NBPXMLParser) -> None:
    test_cases = [
        ("2024-01-01", date(2024, 1, 1)),
        ("2024-12-31", date(2024, 12, 31)),
        ("2023-06-15", date(2023, 6, 15)),
        ("2025-02-28", date(2025, 2, 28)),
    ]

    for date_str, expected_date in test_cases:
        scraped = NBPScrapedData(rate_value="5.75", effective_date_str=date_str)
        _, effective_date = parser.convert_to_domain(scraped)
        assert effective_date == expected_date


def test_convert_invalid_rate_value(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="not_a_number", effective_date_str="2024-01-15")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid rate value: not_a_number" in str(exc_info.value)


def test_convert_empty_rate_value(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="", effective_date_str="2024-01-15")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid rate value" in str(exc_info.value)


def test_convert_invalid_date_format(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="15-01-2024")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid date format: 15-01-2024" in str(exc_info.value)


def test_convert_invalid_date_value(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="not_a_date")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid date format: not_a_date" in str(exc_info.value)


def test_convert_empty_date(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid date format" in str(exc_info.value)


def test_convert_date_with_invalid_month(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-13-01")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid date format" in str(exc_info.value)


def test_convert_date_with_invalid_day(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-02-30")

    with pytest.raises(ValueError) as exc_info:
        parser.convert_to_domain(scraped)

    assert "Invalid date format" in str(exc_info.value)


def test_convert_preserves_decimal_precision(parser: NBPXMLParser) -> None:
    test_cases = [
        "5.75",
        "0.01",
        "10.125",
        "7.5555",
    ]

    for rate_str in test_cases:
        scraped = NBPScrapedData(rate_value=rate_str, effective_date_str="2024-01-01")
        rate, _ = parser.convert_to_domain(scraped)
        assert str(rate) == rate_str


def test_convert_rate_with_multiple_commas(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="5,7,5", effective_date_str="2024-01-01")

    with pytest.raises(ValueError):
        parser.convert_to_domain(scraped)


def test_convert_negative_rate(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="-1.5", effective_date_str="2024-01-01")

    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("-1.5")
    assert effective_date == date(2024, 1, 1)


def test_convert_zero_rate(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="0", effective_date_str="2024-01-01")

    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("0")
    assert effective_date == date(2024, 1, 1)


def test_convert_large_rate(parser: NBPXMLParser) -> None:
    scraped = NBPScrapedData(rate_value="999.99", effective_date_str="2024-01-01")

    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("999.99")
    assert effective_date == date(2024, 1, 1)


def test_parse_and_convert_workflow(parser: NBPXMLParser, valid_xml: str) -> None:
    scraped = parser.parse(valid_xml)

    assert isinstance(scraped, NBPScrapedData)

    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)


def test_parse_and_convert_with_comma(
    parser: NBPXMLParser, valid_xml_with_comma: str
) -> None:
    scraped = parser.parse(valid_xml_with_comma)
    rate, effective_date = parser.convert_to_domain(scraped)

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)


def test_end_to_end_real_world_scenario(parser: NBPXMLParser) -> None:
    real_world_xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <tabela>
        <numer_tabeli>A/001/2024</numer_tabeli>
        <data_publikacji>2024-01-15</data_publikacji>
    </tabela>
    <pozycja id="ref" oprocentowanie="5,75" obowiazuje_od="2024-01-15">
        <opis>Stopa referencyjna</opis>
    </pozycja>
    <pozycja id="lomb" oprocentowanie="6,25" obowiazuje_od="2024-01-15">
        <opis>Stopa lombardowa</opis>
    </pozycja>
</stopy_procentowe>"""

    scraped = parser.parse(real_world_xml)
    assert scraped.rate_value == "5,75"

    rate, effective_date = parser.convert_to_domain(scraped)
    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)


def test_parse_is_static() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<stopy_procentowe>
    <pozycja id="ref" oprocentowanie="5.75" obowiazuje_od="2024-01-15"/>
</stopy_procentowe>"""

    result = NBPXMLParser.parse(xml)
    assert isinstance(result, NBPScrapedData)


def test_convert_to_domain_is_static() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    rate, effective_date = NBPXMLParser.convert_to_domain(scraped)

    assert rate == Decimal("5.75")
    assert effective_date == date(2024, 1, 15)

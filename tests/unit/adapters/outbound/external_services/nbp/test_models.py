from dataclasses import fields

from src.adapters.outbound.external_services.nbp.models import NBPScrapedData


def test_is_dataclass() -> None:
    assert hasattr(NBPScrapedData, "__dataclass_fields__")


def test_has_rate_value_field() -> None:
    field_names = [f.name for f in fields(NBPScrapedData)]
    assert "rate_value" in field_names


def test_has_effective_date_str_field() -> None:
    field_names = [f.name for f in fields(NBPScrapedData)]
    assert "effective_date_str" in field_names


def test_has_exactly_two_fields() -> None:
    assert len(fields(NBPScrapedData)) == 2


def test_fields_are_strings() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    assert isinstance(scraped.rate_value, str)
    assert isinstance(scraped.effective_date_str, str)


def test_create_with_valid_data() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    assert scraped.rate_value == "5.75"
    assert scraped.effective_date_str == "2024-01-15"


def test_create_with_comma_separator() -> None:
    scraped = NBPScrapedData(rate_value="5,75", effective_date_str="2024-01-15")

    assert scraped.rate_value == "5,75"
    assert scraped.effective_date_str == "2024-01-15"


def test_create_with_different_date_formats() -> None:
    test_cases = [
        "2024-01-15",
        "2023-12-31",
        "2025-06-30",
    ]

    for date_str in test_cases:
        scraped = NBPScrapedData(rate_value="5.75", effective_date_str=date_str)
        assert scraped.effective_date_str == date_str


def test_create_with_various_rate_values() -> None:
    test_cases = [
        "0.50",
        "10.00",
        "7,25",
        "15.5",
        "0",
    ]

    for rate in test_cases:
        scraped = NBPScrapedData(rate_value=rate, effective_date_str="2024-01-01")
        assert scraped.rate_value == rate


def test_create_with_empty_strings() -> None:
    scraped = NBPScrapedData(rate_value="", effective_date_str="")

    assert scraped.rate_value == ""
    assert scraped.effective_date_str == ""


def test_create_with_whitespace() -> None:
    scraped = NBPScrapedData(rate_value=" 5.75 ", effective_date_str=" 2024-01-15 ")

    assert scraped.rate_value == " 5.75 "
    assert scraped.effective_date_str == " 2024-01-15 "


def test_create_with_keyword_arguments() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    assert scraped.rate_value == "5.75"
    assert scraped.effective_date_str == "2024-01-15"


def test_create_with_positional_arguments() -> None:
    scraped = NBPScrapedData("5.75", "2024-01-15")

    assert scraped.rate_value == "5.75"
    assert scraped.effective_date_str == "2024-01-15"


def test_equal_instances() -> None:
    scraped1 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    scraped2 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    assert scraped1 == scraped2


def test_different_rate_not_equal() -> None:
    scraped1 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    scraped2 = NBPScrapedData(rate_value="6.00", effective_date_str="2024-01-15")

    assert scraped1 != scraped2


def test_different_date_not_equal() -> None:
    scraped1 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    scraped2 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-16")

    assert scraped1 != scraped2


def test_not_equal_to_none() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    assert scraped is not None


def test_not_equal_to_different_type() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    assert scraped != "not a scraped data"
    assert scraped != {"rate_value": "5.75", "effective_date_str": "2024-01-15"}


def test_repr_contains_class_name() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    repr_str = repr(scraped)

    assert "NBPScrapedData" in repr_str


def test_repr_contains_rate_value() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    repr_str = repr(scraped)

    assert "rate_value" in repr_str
    assert "5.75" in repr_str


def test_repr_contains_effective_date_str() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    repr_str = repr(scraped)

    assert "effective_date_str" in repr_str
    assert "2024-01-15" in repr_str


def test_repr_is_evaluable() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    repr_str = repr(scraped)
    recreated = eval(repr_str)

    assert recreated == scraped


def test_can_access_rate_value() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    assert scraped.rate_value == "5.75"


def test_can_access_effective_date_str() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    assert scraped.effective_date_str == "2024-01-15"


def test_can_modify_rate_value() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    scraped.rate_value = "6.00"

    assert scraped.rate_value == "6.00"


def test_can_modify_effective_date_str() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    scraped.effective_date_str = "2024-02-01"

    assert scraped.effective_date_str == "2024-02-01"


def test_use_as_intermediate_data_structure() -> None:
    raw_rate = "5,75"
    raw_date = "2024-01-15"

    scraped = NBPScrapedData(rate_value=raw_rate, effective_date_str=raw_date)

    assert scraped.rate_value == raw_rate
    assert scraped.effective_date_str == raw_date


def test_multiple_instances_independent() -> None:
    scraped1 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    scraped2 = NBPScrapedData(rate_value="6.00", effective_date_str="2024-02-01")

    scraped1.rate_value = "7.00"

    assert scraped2.rate_value == "6.00"


def test_can_be_used_in_collections() -> None:
    scraped1 = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")
    scraped2 = NBPScrapedData(rate_value="6.00", effective_date_str="2024-02-01")
    scraped3 = NBPScrapedData(rate_value="5.50", effective_date_str="2024-03-01")

    scraped_list = [scraped1, scraped2, scraped3]
    assert len(scraped_list) == 3


def test_can_be_unpacked() -> None:
    scraped = NBPScrapedData(rate_value="5.75", effective_date_str="2024-01-15")

    rate = scraped.rate_value
    date = scraped.effective_date_str

    assert rate == "5.75"
    assert date == "2024-01-15"


def test_very_long_strings() -> None:
    long_rate = "5" * 1000
    long_date = "2024-01-15" * 100

    scraped = NBPScrapedData(rate_value=long_rate, effective_date_str=long_date)

    assert scraped.rate_value == long_rate
    assert scraped.effective_date_str == long_date


def test_special_characters_in_strings() -> None:
    special_rate = "5.75\n\t"
    special_date = "2024-01-15\x00"

    scraped = NBPScrapedData(rate_value=special_rate, effective_date_str=special_date)

    assert scraped.rate_value == special_rate
    assert scraped.effective_date_str == special_date


def test_unicode_characters() -> None:
    scraped = NBPScrapedData(rate_value="5.75€", effective_date_str="2024-01-15日")

    assert scraped.rate_value == "5.75€"
    assert scraped.effective_date_str == "2024-01-15日"

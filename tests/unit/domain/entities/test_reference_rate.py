from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.reference_rate import ReferenceRate


@pytest.fixture
def l_ref_rate() -> ReferenceRate:
    return ReferenceRate(
        id=uuid4(), value=Decimal("2.0"), start_date=datetime.now().date()
    )


def test_create_success() -> None:
    value = Decimal("1.0")
    start_date = datetime.now().date()

    ref_rate = ReferenceRate.create(value=value, start_date=start_date)

    assert ref_rate.value == value
    assert ref_rate.start_date == start_date


def test_validate_success(l_ref_rate: ReferenceRate) -> None:
    l_ref_rate.validate()


def test_validate_value_type_failure(l_ref_rate: ReferenceRate) -> None:
    l_ref_rate.value = 1.0  # type: ignore
    assert not isinstance(l_ref_rate.value, Decimal)
    with pytest.raises(TypeError, match="Reference rate value must be a Decimal."):
        l_ref_rate._validate_ref_rate_value()


def test_validate_value_value_failure(l_ref_rate: ReferenceRate) -> None:
    l_ref_rate.value = Decimal("-1.0")
    assert l_ref_rate.value < Decimal("0.0")
    with pytest.raises(ValueError, match="Reference rate value cannot be negative."):
        l_ref_rate._validate_ref_rate_value()

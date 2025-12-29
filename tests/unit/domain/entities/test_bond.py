from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4, UUID

import pytest

from src.domain.entities.bond import Bond
from src.domain.exceptions import ValidationError


@pytest.fixture
def local_bond() -> Bond:
    return Bond(
        id=uuid4(),
        series="TEST_SERIES",
        nominal_value=Decimal(500),
        maturity_period=12,
        initial_interest_rate=Decimal(4.25),
        first_interest_period=5,
        reference_rate_margin=Decimal(0.5),
    )


def test_bond_creation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_validate = MagicMock()
    monkeypatch.setattr(Bond, "validate", mock_validate)

    bond = Bond.create(
        series="TEST_SERIES",
        nominal_value=Decimal(1000),
        maturity_period=24,
        initial_interest_rate=Decimal(5.0),
        first_interest_period=6,
        reference_rate_margin=Decimal(1.0),
    )

    assert bond.id is not None
    assert isinstance(bond.id, UUID)
    assert bond.id.version == 4
    assert bond.series == "TEST_SERIES"
    assert bond.nominal_value == Decimal(1000)
    assert bond.maturity_period == 24
    assert bond.initial_interest_rate == Decimal(5.0)
    assert bond.first_interest_period == 6
    assert bond.reference_rate_margin == Decimal(1.0)

    mock_validate.assert_called_once()


def test_bond_create_wrong_field_type() -> None:
    with pytest.raises(
        ValidationError, match="Bond nominal_value must be of type Decimal."
    ):
        Bond.create(
            series="TEST_SERIES",
            nominal_value=1000,  # type: ignore[arg-type]
            maturity_period=24,
            initial_interest_rate=Decimal(5.0),
            first_interest_period=6,
            reference_rate_margin=Decimal(1.0),
        )
    with pytest.raises(
        ValidationError, match="Bond initial_interest_rate must be of type Decimal."
    ):
        Bond.create(
            series="TEST_SERIES",
            nominal_value=Decimal(1000),
            maturity_period=24,
            initial_interest_rate=5.0,  # type: ignore[arg-type]
            first_interest_period=6,
            reference_rate_margin=Decimal(1.0),
        )
    with pytest.raises(
        ValidationError, match="Bond reference_rate_margin must be of type Decimal."
    ):
        Bond.create(
            series="TEST_SERIES",
            nominal_value=Decimal(1000),
            maturity_period=24,
            initial_interest_rate=Decimal(5.0),
            first_interest_period=6,
            reference_rate_margin=1.0,  # type: ignore[arg-type]
        )


def test_bond_validate(monkeypatch: pytest.MonkeyPatch, local_bond: Bond) -> None:
    mock_validate_nominal_value = MagicMock()
    mock_validate_maturity_period = MagicMock()
    mock_validate_initial_interest_rate = MagicMock()
    mock_validate_types = MagicMock()

    monkeypatch.setattr(
        local_bond, "_validate_nominal_value", mock_validate_nominal_value
    )
    monkeypatch.setattr(
        local_bond, "_validate_maturity_period", mock_validate_maturity_period
    )
    monkeypatch.setattr(
        local_bond,
        "_validate_initial_interest_rate",
        mock_validate_initial_interest_rate,
    )
    monkeypatch.setattr(local_bond, "_validate_types", mock_validate_types)

    local_bond.validate()

    mock_validate_nominal_value.assert_called_once()
    mock_validate_maturity_period.assert_called_once_with()
    mock_validate_initial_interest_rate.assert_called_once_with()
    mock_validate_types.assert_called_once_with()


def test_validate_nominal_value_success(local_bond: Bond) -> None:
    local_bond.nominal_value = Decimal(1000)
    local_bond._validate_nominal_value()


def test_validate_nominal_value_failure(local_bond: Bond) -> None:
    local_bond.nominal_value = Decimal(0)
    with pytest.raises(
        ValidationError, match="Bond nominal_value must be greater than 0."
    ):
        local_bond._validate_nominal_value()

    local_bond.nominal_value = Decimal(-100)
    with pytest.raises(
        ValidationError, match="Bond nominal_value must be greater than 0."
    ):
        local_bond._validate_nominal_value()


def test_validate_maturity_period_success(local_bond: Bond) -> None:
    local_bond.maturity_period = 24
    local_bond._validate_maturity_period()


def test_validate_maturity_period_failure(local_bond: Bond) -> None:
    local_bond.maturity_period = 0
    with pytest.raises(
        ValidationError, match="Bond maturity_period must be greater than 0."
    ):
        local_bond._validate_maturity_period()

    local_bond.maturity_period = -12
    with pytest.raises(
        ValidationError, match="Bond maturity_period must be greater than 0."
    ):
        local_bond._validate_maturity_period()


def test_validate_initial_interest_rate_success(local_bond: Bond) -> None:
    local_bond.initial_interest_rate = Decimal(3.5)
    local_bond._validate_initial_interest_rate()


def test_validate_initial_interest_rate_failure(local_bond: Bond) -> None:
    local_bond.initial_interest_rate = Decimal(0)
    with pytest.raises(
        ValidationError, match="Bond initial_interest_rate must be greater than 0."
    ):
        local_bond._validate_initial_interest_rate()

    local_bond.initial_interest_rate = Decimal(-2.0)
    with pytest.raises(
        ValidationError, match="Bond initial_interest_rate must be greater than 0."
    ):
        local_bond._validate_initial_interest_rate()

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

import pytest

from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder
from src.domain.entities.reference_rate import ReferenceRate
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


@pytest.fixture
def sample_bond() -> Bond:
    return Bond.create(
        series="ROR1111",
        nominal_value=Decimal("100"),
        maturity_period=12,
        initial_interest_rate=Decimal("4.75"),
        first_interest_period=1,
        reference_rate_margin=Decimal("0.1"),
    )


@pytest.fixture
def sample_bondholder(sample_bond: Bond) -> BondHolder:
    return BondHolder.create(
        user_id=uuid4(),
        bond_id=sample_bond.id,
        quantity=10,
        purchase_date=date(2024, 1, 15),
    )


@pytest.fixture
def sample_reference_rate() -> ReferenceRate:
    return ReferenceRate(
        id=uuid4(),
        value=Decimal("5.75"),
        start_date=date(2024, 1, 1),
    )


@pytest.fixture
def calculator(
    sample_bondholder: BondHolder,
    sample_bond: Bond,
) -> BondHolderIncomeCalculator:
    return BondHolderIncomeCalculator()


def _calculate_regular_gross_bond_income(
    bond: Bond,
    calculator: BondHolderIncomeCalculator,
    days_in_period: int,
    reference_rate_value: Decimal,
) -> Decimal:
    annual_rate = calculator._from_percent(
        reference_rate_value
    ) + calculator._from_percent(bond.reference_rate_margin)
    gross_interest_per_bond = (
        bond.nominal_value * annual_rate * days_in_period / Decimal("365")
    )
    return gross_interest_per_bond.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _calculate_interest_gross_bond_income(
    bond: Bond,
    calculator: BondHolderIncomeCalculator,
    days_in_period: int,
) -> Decimal:
    daily_rate = (
        bond.nominal_value
        * calculator._from_percent(bond.initial_interest_rate)
        * days_in_period
        / Decimal("365")
    )
    return daily_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def test_calculate_month_bondholder_income_regular_period(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:
    tested_income = calculator.calculate_monthly_bh_income(
        bondholder=sample_bondholder,
        bond=sample_bond,
        reference_rate=sample_reference_rate,
    )
    days_in_period = calculator._days_in_period(
        purchase_date=sample_bondholder.purchase_date
    )
    gross_per_bond = _calculate_regular_gross_bond_income(
        bond=sample_bond,
        calculator=calculator,
        days_in_period=days_in_period,
        reference_rate_value=sample_reference_rate.value,
    )
    expected = gross_per_bond * Decimal("0.81") * sample_bondholder.quantity

    assert tested_income == expected


def test_calculate_month_bondholder_income_interest_period(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:
    payment_date = sample_bondholder.purchase_date + timedelta(days=10)

    tested_income = calculator.calculate_monthly_bh_income(
        bondholder=sample_bondholder,
        bond=sample_bond,
        reference_rate=sample_reference_rate,
        day=payment_date,
    )
    days_in_period = calculator._days_in_period(
        purchase_date=sample_bondholder.purchase_date
    )
    gross_per_bond = _calculate_interest_gross_bond_income(
        bond=sample_bond,
        calculator=calculator,
        days_in_period=days_in_period,
    )

    expected = gross_per_bond * Decimal("0.81") * sample_bondholder.quantity

    assert tested_income == expected


def test_calculate_interest_income_correct_rounding(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
) -> None:
    days_in_period = calculator._days_in_period(
        purchase_date=sample_bondholder.purchase_date
    )
    tested_income = calculator._calculate_interest_income(
        days_in_month=days_in_period,
        bond=sample_bond,
        quantity=sample_bondholder.quantity,
    )

    gross_per_bond = _calculate_interest_gross_bond_income(
        bond=sample_bond,
        calculator=calculator,
        days_in_period=days_in_period,
    )
    net_per_bond = gross_per_bond * Decimal("0.81")
    expected_net_for_bondholder = net_per_bond * sample_bondholder.quantity

    assert tested_income == expected_net_for_bondholder


def test_calculate_regular_income_with_different_margins(
    calculator: BondHolderIncomeCalculator,
    sample_bondholder: BondHolder,
    sample_reference_rate: ReferenceRate,
) -> None:
    bond_high_margin = Bond.create(
        series="ROR2222",
        maturity_period=36,
        nominal_value=Decimal("100.00"),
        initial_interest_rate=Decimal("6.00"),
        reference_rate_margin=Decimal("1.00"),
        first_interest_period=3,
    )
    days_in_period = calculator._days_in_period(
        purchase_date=sample_bondholder.purchase_date
    )
    tested_income = calculator._calculate_regular_income(
        bond=bond_high_margin,
        reference_rate=sample_reference_rate.value,
        quantity=sample_bondholder.quantity,
        days_in_month=days_in_period,
    )

    gross_regular_income = _calculate_regular_gross_bond_income(
        bond=bond_high_margin,
        calculator=calculator,
        days_in_period=days_in_period,
        reference_rate_value=sample_reference_rate.value,
    )
    expected_net_regular_income = gross_regular_income * Decimal("0.81")
    expected = expected_net_regular_income * sample_bondholder.quantity

    assert tested_income == expected


def test_from_percent_conversion(
    calculator: BondHolderIncomeCalculator,
) -> None:
    assert calculator._from_percent(Decimal("5.00")) == Decimal("0.05")
    assert calculator._from_percent(Decimal("10.50")) == Decimal("0.105")
    assert calculator._from_percent(Decimal("0.25")) == Decimal("0.0025")


@pytest.mark.parametrize(
    "purchase_date, current_date, expected_days",
    [
        (date(2025, 4, 15), date(2025, 4, 20), 30),
        (date(2025, 4, 15), date(2025, 5, 20), 31),
        (date(2025, 2, 15), date(2025, 3, 10), 28),
        (date(2024, 1, 31), date(2024, 2, 15), 29),
    ],
)
def test_days_in_period_standard_month(
    calculator: BondHolderIncomeCalculator,
    purchase_date: date,
    current_date: date,
    expected_days: int,
) -> None:
    tested_days = calculator._days_in_period(
        purchase_date=purchase_date, today=current_date
    )
    assert tested_days == expected_days


def test_calculate_bh_income_for_period_single_rate(
    sample_bondholder: BondHolder,
    sample_bond: Bond,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:
    start_date = date(2024, 2, 1)
    end_date = date(2024, 4, 30)

    result = calculator.calculate_bh_income_for_period(
        bondholder=sample_bondholder,
        bond=sample_bond,
        reference_rates=[sample_reference_rate],
        start_date=start_date,
        end_date=end_date,
        purchase_date=sample_bondholder.purchase_date,
    )

    assert len(result) == 3
    assert date(2024, 2, 15) in result
    assert date(2024, 3, 15) in result
    assert date(2024, 4, 15) in result

    for income in result.values():
        assert isinstance(income, Decimal)
        assert income > 0


def test_calculate_bh_income_for_period_multiple_rates(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
) -> None:
    calculator = BondHolderIncomeCalculator()

    rates = [
        ReferenceRate(id=uuid4(), value=Decimal("5.75"), start_date=date(2024, 1, 1)),
        ReferenceRate(id=uuid4(), value=Decimal("6.00"), start_date=date(2024, 3, 1)),
        ReferenceRate(id=uuid4(), value=Decimal("5.50"), start_date=date(2024, 5, 1)),
    ]

    start_date = date(2024, 2, 1)
    end_date = date(2024, 6, 30)

    result = calculator.calculate_bh_income_for_period(
        bondholder=sample_bondholder,
        bond=sample_bond,
        reference_rates=rates,
        start_date=start_date,
        end_date=end_date,
        purchase_date=sample_bondholder.purchase_date,
    )

    assert len(result) == 5

    assert result[date(2024, 3, 15)] != result[date(2024, 6, 15)]


def test_calculate_bh_income_for_period_no_overlap(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:
    start_date = date(2024, 1, 16)
    end_date = date(2024, 2, 10)

    result = calculator.calculate_bh_income_for_period(
        bondholder=sample_bondholder,
        bond=sample_bond,
        reference_rates=[sample_reference_rate],
        start_date=start_date,
        end_date=end_date,
        purchase_date=sample_bondholder.purchase_date,
    )

    assert len(result) == 0


def test_calculate_bh_income_for_period_exact_boundaries(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:

    start_date = date(2024, 2, 15)
    end_date = date(2024, 2, 15)

    result = calculator.calculate_bh_income_for_period(
        bond=sample_bond,
        bondholder=sample_bondholder,
        purchase_date=sample_bondholder.purchase_date,
        reference_rates=[sample_reference_rate],
        start_date=start_date,
        end_date=end_date,
    )

    assert len(result) == 1
    assert date(2024, 2, 15) in result


def test_calculate_bh_income_for_period_missing_rate_raises_error(
    sample_bond: Bond,
    sample_bondholder: BondHolder,
    calculator: BondHolderIncomeCalculator,
) -> None:

    rate = ReferenceRate(id=uuid4(), value=Decimal("5.75"), start_date=date(2024, 3, 1))

    start_date = date(2024, 2, 1)
    end_date = date(2024, 4, 30)

    with pytest.raises(ValueError, match="No reference rate found for payment date"):
        calculator.calculate_bh_income_for_period(
            bond=sample_bond,
            bondholder=sample_bondholder,
            purchase_date=sample_bondholder.purchase_date,
            reference_rates=[rate],
            start_date=start_date,
            end_date=end_date,
        )


def test_zero_quantity_bondholder(
    sample_bond: Bond,
    calculator: BondHolderIncomeCalculator,
    sample_reference_rate: ReferenceRate,
) -> None:
    bondholder_zero = BondHolder(
        id=uuid4(),
        user_id=uuid4(),
        bond_id=uuid4(),
        quantity=0,
        purchase_date=date(2024, 1, 15),
    )

    payment_date = date(2024, 3, 15)

    income = calculator.calculate_monthly_bh_income(
        bondholder=bondholder_zero,
        bond=sample_bond,
        reference_rate=sample_reference_rate,
        day=payment_date,
    )

    assert income == Decimal("0")


def test_days_in_period() -> None:
    purchase_date = date(2025, 9, 15)
    today = date(2025, 8, 20)

    days = BondHolderIncomeCalculator._days_in_period(purchase_date, today)

    assert days == 31

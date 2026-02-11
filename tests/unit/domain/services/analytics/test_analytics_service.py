from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.domain.entities.bondholder import BondHolder
from src.domain.services.analytics.analytics_service import AnalyticsService

def _create_bondholder(purchase_date: date, quantity: int) -> BondHolder:
    return BondHolder(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=quantity,
        purchase_date=purchase_date,
        last_update=None,
    )
    
@pytest.fixture
def service() -> AnalyticsService:
    return AnalyticsService()


def test_determine_time_interval_returns_5_days_for_30_day_range(
    service: AnalyticsService,
) -> None:
    first = date(2024, 1, 1)
    last = date(2024, 1, 31)

    result = service._determine_time_interval(first, last)

    assert result == timedelta(days=5)


def test_determine_time_interval_returns_2_weeks_for_91_day_range(
    service: AnalyticsService,
) -> None:
    first = date(2024, 1, 1)
    last = date(2024, 4, 1)

    result = service._determine_time_interval(first, last)

    assert result == timedelta(weeks=2)


def test_determine_time_interval_returns_2_weeks_for_180_day_range(
    service: AnalyticsService,
) -> None:
    first = date(2024, 1, 1)
    last = date(2024, 6, 29)

    result = service._determine_time_interval(first, last)

    assert result == timedelta(weeks=2)


def test_determine_time_interval_returns_4_weeks_for_365_day_range(
    service: AnalyticsService,
) -> None:
    first = date(2024, 1, 1)
    last = date(2024, 12, 31)

    result = service._determine_time_interval(first, last)

    assert result == timedelta(weeks=4)


def test_determine_time_interval_returns_default_for_range_over_365_days(
    service: AnalyticsService,
) -> None:
    first = date(2023, 1, 1)
    last = date(2025, 1, 1)

    result = service._determine_time_interval(first, last)

    assert result == timedelta(days=30)


def test_determine_time_interval_uses_threshold_inclusively(
    service: AnalyticsService,
) -> None:
    # exactly on the boundary of 30 days — should still return 5 days
    first = date(2024, 1, 1)
    last = date(2024, 1, 31)  # exactly 30 days

    result = service._determine_time_interval(first, last)

    assert result == timedelta(days=5)


def test_find_timeline_points_includes_first_and_last_dates() -> None:
    first = date(2024, 1, 1)
    last = date(2024, 1, 11)
    interval = timedelta(days=5)

    result = AnalyticsService._find_timeline_points(first, last, interval)

    assert result[0] == first
    assert result[-1] == last


def test_find_timeline_points_appends_last_date_when_not_naturally_reached() -> None:
    first = date(2024, 1, 1)
    last = date(2024, 1, 8)
    interval = timedelta(days=5)

    result = AnalyticsService._find_timeline_points(first, last, interval)

    assert result == [date(2024, 1, 1), date(2024, 1, 6), date(2024, 1, 8)]


def test_find_timeline_points_does_not_duplicate_last_date_when_naturally_reached() -> (
    None
):
    first = date(2024, 1, 1)
    last = date(2024, 1, 6)
    interval = timedelta(days=5)

    result = AnalyticsService._find_timeline_points(first, last, interval)

    assert result.count(last) == 1


def test_find_timeline_points_returns_only_one_point_when_first_equals_last() -> None:
    single = date(2024, 1, 1)

    result = AnalyticsService._find_timeline_points(single, single, timedelta(days=5))

    assert result == [single]


def test_get_equity_history_returns_zero_equity_before_any_purchase(
    service: AnalyticsService,
) -> None:
    today = date.today()
    bh = _create_bondholder(purchase_date=today, quantity=10)
    face_value = Decimal("1000")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history([(bh, face_value)])

    # первая точка — дата покупки, equity уже включает её
    assert result[0][1] == Decimal("10000")


def test_get_equity_history_equity_grows_when_bondholder_added_later(
    service: AnalyticsService,
) -> None:
    today = date.today()
    early_bh = _create_bondholder(purchase_date=today - timedelta(days=20), quantity=5)
    late_bh = _create_bondholder(purchase_date=today, quantity=3)
    face_value = Decimal("1000")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history(
            [(early_bh, face_value), (late_bh, face_value)]
        )

    first_equity = result[0][1]
    last_equity = result[-1][1]
    assert last_equity > first_equity


def test_get_equity_history_equity_never_decreases(
    service: AnalyticsService,
) -> None:
    today = date.today()
    bh1 = _create_bondholder(purchase_date=today - timedelta(days=25), quantity=2)
    bh2 = _create_bondholder(purchase_date=today - timedelta(days=10), quantity=4)
    face_value = Decimal("500")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history(
            [(bh1, face_value), (bh2, face_value)]
        )

    equities = [equity for _, equity in result]
    assert equities == sorted(equities)


def test_get_equity_history_total_equity_equals_sum_of_all_bondholders(
    service: AnalyticsService,
) -> None:
    today = date.today()
    bh1 = _create_bondholder(purchase_date=today - timedelta(days=20), quantity=3)
    bh2 = _create_bondholder(purchase_date=today - timedelta(days=10), quantity=7)
    face_value = Decimal("200")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history(
            [(bh1, face_value), (bh2, face_value)]
        )

    expected_total = (bh1.quantity + bh2.quantity) * face_value
    assert result[-1][1] == expected_total


def test_get_equity_history_bondholders_with_same_purchase_date_accumulated_in_one_point(
    service: AnalyticsService,
) -> None:
    today = date.today()
    same_date = today - timedelta(days=10)
    bh1 = _create_bondholder(purchase_date=same_date, quantity=2)
    bh2 = _create_bondholder(purchase_date=same_date, quantity=3)
    face_value = Decimal("100")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history(
            [(bh1, face_value), (bh2, face_value)]
        )
    assert result[0][1] == Decimal("500")


def test_get_equity_history_result_is_sorted_by_date(
    service: AnalyticsService,
) -> None:
    today = date.today()
    bh1 = _create_bondholder(purchase_date=today - timedelta(days=25), quantity=1)
    bh2 = _create_bondholder(purchase_date=today - timedelta(days=5), quantity=1)
    face_value = Decimal("1000")

    with patch("src.domain.services.analytics.analytics_service.datetime") as mock_dt:
        mock_dt.now.return_value.date.return_value = today
        result = service.get_equity_history(
            [(bh1, face_value), (bh2, face_value)]
        )

    dates = [d for d, _ in result]
    assert dates == sorted(dates)

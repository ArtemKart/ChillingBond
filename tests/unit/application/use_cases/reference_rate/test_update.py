from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from src.adapters.outbound.external_services.nbp.fetcher import NBPXMLFetcher
from src.adapters.outbound.external_services.nbp.nbp_data_provider import (
    NBPDataProvider,
)
from src.adapters.outbound.external_services.nbp.parser import NBPXMLParser
from src.application.use_cases.reference_rate.update import UpdateReferenceRateUseCase
from src.domain.entities.reference_rate import ReferenceRate as ReferenceRateEntity


@pytest.fixture
def nbp_provider_mock() -> AsyncMock:
    mock = AsyncMock(spec=NBPDataProvider)
    mock.fetcher = AsyncMock(spec=NBPXMLFetcher)
    mock.parser = Mock(spec=NBPXMLParser)
    return mock


@pytest.fixture
def use_case(
    mock_reference_rate_repo: AsyncMock,
    nbp_provider_mock: AsyncMock,
) -> UpdateReferenceRateUseCase:
    return UpdateReferenceRateUseCase(
        reference_rate_repo=mock_reference_rate_repo,
        rate_provider=nbp_provider_mock,
    )


async def test_no_rate_in_db_saves_new_rate(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test saving new rate when database is empty."""
    current_rate = Decimal("5.75")
    effective_date = date(2025, 1, 15)

    nbp_provider_mock.get_current_rate.return_value = (
        current_rate,
        effective_date,
    )
    mock_reference_rate_repo.get_latest.return_value = None
    mock_reference_rate_repo.save = AsyncMock()
    mock_reference_rate_repo.update = AsyncMock()

    result = await use_case.execute()

    assert result.success is True
    assert result.rate_changed is True
    assert result.message == "New rate detected and saved."
    assert result.rate_value == current_rate
    assert result.effective_date == effective_date

    mock_reference_rate_repo.save.assert_called_once()
    mock_reference_rate_repo.update.assert_not_called()


async def test_rate_not_changed(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test when current rate matches database rate."""
    current_rate = Decimal("5.75")
    effective_date = date(2025, 1, 15)

    existing_rate = ReferenceRateEntity(
        id=uuid4(),
        value=current_rate,
        start_date=effective_date,
        end_date=None,
    )

    nbp_provider_mock.get_current_rate.return_value = (
        current_rate,
        effective_date,
    )
    mock_reference_rate_repo.get_latest.return_value = existing_rate
    mock_reference_rate_repo.save = AsyncMock()
    mock_reference_rate_repo.update = AsyncMock()

    result = await use_case.execute()

    assert result.success is True
    assert result.rate_changed is False
    assert result.message == "Rate has not changed"
    assert result.rate_value == current_rate
    assert result.effective_date == effective_date

    mock_reference_rate_repo.save.assert_not_called()
    mock_reference_rate_repo.update.assert_not_called()


async def test_rate_value_changed_updates_old_and_saves_new(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test when rate value changes."""
    fake_today = datetime(2025, 1, 26, 10, 0, 0)

    old_rate = Decimal("5.75")
    new_rate = Decimal("6.00")
    old_date = date(2024, 12, 1)
    new_date = date(2025, 1, 15)

    existing_rate = ReferenceRateEntity(
        id=uuid4(),
        value=old_rate,
        start_date=old_date,
        end_date=None,
    )

    nbp_provider_mock.get_current_rate.return_value = (new_rate, new_date)
    mock_reference_rate_repo.get_latest.return_value = existing_rate
    mock_reference_rate_repo.update = AsyncMock()
    mock_reference_rate_repo.save = AsyncMock()

    with patch(
        "src.application.use_cases.reference_rate.update.datetime"
    ) as mock_datetime:
        mock_datetime.today.return_value = fake_today
        result = await use_case.execute()

    assert result.success is True
    assert result.rate_changed is True
    assert result.message == "New rate detected and saved."
    assert result.rate_value == new_rate
    assert result.effective_date == new_date

    # Verify old rate was closed
    assert existing_rate.end_date == fake_today
    mock_reference_rate_repo.update.assert_called_once_with(existing_rate)

    # Verify new rate was saved
    mock_reference_rate_repo.save.assert_called_once()
    saved_rate = mock_reference_rate_repo.save.call_args[1]["ref_rate"]
    assert saved_rate.value == new_rate
    assert saved_rate.start_date == new_date


async def test_effective_date_changed_updates_old_and_saves_new(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test when effective date changes but value stays the same."""
    fake_today = datetime(2025, 1, 26, 15, 30, 0)

    rate_value = Decimal("5.75")
    old_date = date(2025, 1, 1)
    new_date = date(2025, 1, 15)

    existing_rate = ReferenceRateEntity(
        id=uuid4(),
        value=rate_value,
        start_date=old_date,
        end_date=None,
    )

    nbp_provider_mock.get_current_rate.return_value = (rate_value, new_date)
    mock_reference_rate_repo.get_latest.return_value = existing_rate
    mock_reference_rate_repo.update = AsyncMock()
    mock_reference_rate_repo.save = AsyncMock()

    with patch(
        "src.application.use_cases.reference_rate.update.datetime"
    ) as mock_datetime:
        mock_datetime.today.return_value = fake_today
        result = await use_case.execute()

    assert result.success is True
    assert result.rate_changed is True
    assert existing_rate.end_date == fake_today
    mock_reference_rate_repo.update.assert_called_once_with(existing_rate)
    mock_reference_rate_repo.save.assert_called_once()


async def test_provider_fails_returns_error(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test error handling when provider fails."""
    nbp_provider_mock.get_current_rate.side_effect = Exception("API connection failed")
    mock_reference_rate_repo.save = AsyncMock()
    mock_reference_rate_repo.update = AsyncMock()

    result = await use_case.execute()

    assert result.success is False
    assert result.rate_changed is False
    assert "Failed to update: API connection failed" in result.message
    assert result.rate_value is None
    assert result.effective_date is None

    mock_reference_rate_repo.save.assert_not_called()
    mock_reference_rate_repo.update.assert_not_called()


async def test_repository_save_fails_returns_error(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test error handling when repository save fails."""

    current_rate = Decimal("5.75")
    effective_date = date(2025, 1, 15)

    nbp_provider_mock.get_current_rate.return_value = (
        current_rate,
        effective_date,
    )
    mock_reference_rate_repo.get_latest.return_value = None
    mock_reference_rate_repo.save.side_effect = Exception("Database error")

    result = await use_case.execute()

    assert result.success is False
    assert result.rate_changed is False
    assert "Failed to update: Database error" in result.message


async def test_repository_update_fails_returns_error(
    use_case: UpdateReferenceRateUseCase,
    nbp_provider_mock: AsyncMock,
    mock_reference_rate_repo: AsyncMock,
) -> None:
    """Test error handling when repository update fails."""
    old_rate = Decimal("5.75")
    new_rate = Decimal("6.00")
    old_date = date(2024, 12, 1)
    new_date = date(2025, 1, 15)

    existing_rate = ReferenceRateEntity(
        id=uuid4(),
        value=old_rate,
        start_date=old_date,
        end_date=None,
    )

    nbp_provider_mock.get_current_rate.return_value = (new_rate, new_date)
    mock_reference_rate_repo.get_latest.return_value = existing_rate
    mock_reference_rate_repo.update.side_effect = Exception("Update failed")

    result = await use_case.execute()

    assert result.success is False
    assert result.rate_changed is False
    assert "Failed to update: Update failed" in result.message


def test_rates_are_same_when_both_match() -> None:
    """Test rates are considered same when value and date match."""
    result = UpdateReferenceRateUseCase._rates_are_same(
        db_rate_value=Decimal("5.75"),
        db_effective_date=date(2025, 1, 15),
        current_rate_value=Decimal("5.75"),
        current_effective_date=date(2025, 1, 15),
    )
    assert result is True


def test_rates_differ_when_value_differs() -> None:
    """Test rates differ when value is different."""
    result = UpdateReferenceRateUseCase._rates_are_same(
        db_rate_value=Decimal("5.75"),
        db_effective_date=date(2025, 1, 15),
        current_rate_value=Decimal("6.00"),
        current_effective_date=date(2025, 1, 15),
    )
    assert result is False


def test_rates_differ_when_date_differs() -> None:
    """Test rates differ when effective date is different."""
    result = UpdateReferenceRateUseCase._rates_are_same(
        db_rate_value=Decimal("5.75"),
        db_effective_date=date(2025, 1, 15),
        current_rate_value=Decimal("5.75"),
        current_effective_date=date(2025, 1, 20),
    )
    assert result is False


def test_rates_differ_when_both_differ() -> None:
    """Test rates differ when both value and date are different."""
    result = UpdateReferenceRateUseCase._rates_are_same(
        db_rate_value=Decimal("5.75"),
        db_effective_date=date(2025, 1, 15),
        current_rate_value=Decimal("6.00"),
        current_effective_date=date(2025, 1, 20),
    )
    assert result is False

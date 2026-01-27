import signal
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.adapters.inbound.scheduler import start_scheduler
from src.adapters.inbound.scheduler.scheduler_container import SchedulerContainer


@pytest.fixture
def mock_scheduler() -> Mock:
    scheduler = Mock()
    scheduler.get_jobs.return_value = []
    scheduler.start = Mock()
    scheduler.shutdown = Mock()
    return scheduler


@pytest.fixture
def mock_container() -> Mock:
    return Mock(spec=SchedulerContainer)


async def test_scheduler_starts_successfully(
    mock_scheduler: Mock,
    mock_container: Mock,
) -> None:
    """Test successful scheduler startup and configuration."""
    with (
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.APScheduler",
            return_value=mock_scheduler,
        ),
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.SchedulerContainer",
            return_value=mock_container,
        ),
        patch("src.adapters.inbound.scheduler.start_scheduler.signal.signal"),
        patch("asyncio.sleep", side_effect=KeyboardInterrupt),
    ):  # Exit immediately

        await start_scheduler.main()

        mock_scheduler.schedule_every_n_days.assert_called_once()
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()
        mock_scheduler.shutdown.assert_called_once()
        mock_container.cleanup.assert_called_once()


async def test_scheduler_registers_signal_handlers(
    mock_scheduler: Mock,
    mock_container: Mock,
) -> None:
    """Test that SIGTERM and SIGINT handlers are registered."""
    with (
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.APScheduler",
            return_value=mock_scheduler,
        ),
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.SchedulerContainer",
            return_value=mock_container,
        ),
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.signal.signal"
        ) as mock_signal,
        patch("asyncio.sleep", side_effect=KeyboardInterrupt),
    ):

        await start_scheduler.main()

        assert mock_signal.call_count == 2
        mock_signal.assert_any_call(signal.SIGTERM, start_scheduler.handle_shutdown)
        mock_signal.assert_any_call(signal.SIGINT, start_scheduler.handle_shutdown)


async def test_scheduler_schedules_correct_jobs(
    mock_scheduler: Mock,
    mock_container: Mock,
) -> None:
    """Test that jobs are scheduled with correct parameters."""
    with (
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.APScheduler",
            return_value=mock_scheduler,
        ),
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.SchedulerContainer",
            return_value=mock_container,
        ),
        patch("src.adapters.inbound.scheduler.start_scheduler.signal.signal"),
        patch("asyncio.sleep", side_effect=KeyboardInterrupt),
    ):

        await start_scheduler.main()

        mock_scheduler.schedule_every_n_days.assert_called_once()
        call_kwargs = mock_scheduler.schedule_every_n_days.call_args[1]
        assert call_kwargs["days"] == 3
        assert call_kwargs["task_id"] == "nbp_reference_rate_updater"

        mock_scheduler.add_job.assert_called_once()
        call_kwargs = mock_scheduler.add_job.call_args[1]
        assert call_kwargs["task_id"] == "health_check"
        assert call_kwargs["hours"] == 1


async def test_scheduler_cleans_up_on_keyboard_interrupt(
    mock_scheduler: Mock,
    mock_container: Mock,
) -> None:
    """Test cleanup happens on KeyboardInterrupt."""
    with (
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.APScheduler",
            return_value=mock_scheduler,
        ),
        patch(
            "src.adapters.inbound.scheduler.start_scheduler.SchedulerContainer",
            return_value=mock_container,
        ),
        patch("src.adapters.inbound.scheduler.start_scheduler.signal.signal"),
        patch("asyncio.sleep", side_effect=KeyboardInterrupt),
    ):

        await start_scheduler.main()

        mock_scheduler.shutdown.assert_called_once()
        mock_container.cleanup.assert_called_once()


@patch("src.adapters.inbound.scheduler.start_scheduler.logger")
def test_health_check_logs_heartbeat(mock_logger: MagicMock) -> None:
    """Test health check logs heartbeat message."""
    start_scheduler.health_check_task()

    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    assert "Scheduler is ALIVE" in log_message


@patch("sys.exit")
@patch("src.adapters.inbound.scheduler.start_scheduler.logger")
def test_handle_shutdown_logs_and_exits(
    mock_logger: MagicMock, mock_exit: MagicMock
) -> None:
    """Test shutdown handler logs message and exits."""
    start_scheduler.handle_shutdown(signal.SIGTERM, None)

    mock_logger.info.assert_called_once()
    assert "shutdown signal" in mock_logger.info.call_args[0][0].lower()
    mock_exit.assert_called_once_with(0)

import asyncio
import logging
from collections.abc import Callable, Coroutine
from datetime import datetime, time
from typing import Any
from unittest.mock import Mock, patch

import pytest
from apscheduler.triggers.interval import IntervalTrigger
from pytest import LogCaptureFixture

from src.adapters.inbound.scheduler.apscheduler import APScheduler
from src.adapters.inbound.scheduler.scheduler_container import SchedulerContainer


@pytest.fixture
def mock_container() -> Mock:
    return Mock(spec=SchedulerContainer)


@pytest.fixture
def scheduler(mock_container: Mock) -> APScheduler:
    return APScheduler(container=mock_container)


@pytest.fixture
async def async_use_case() -> Callable[[], Coroutine[Any, Any, dict[str, str]]]:
    async def factory() -> dict[str, str]:
        await asyncio.sleep(0.01)
        return {"status": "success"}

    return factory


@pytest.fixture
async def failing_use_case() -> Callable[[], Coroutine[Any, Any, None]]:
    async def factory() -> None:
        await asyncio.sleep(0.01)
        raise ValueError("Test error")

    return factory


async def test_wrapper_executes_use_case_successfully(caplog: LogCaptureFixture) -> None:
    result_value = {"status": "completed", "count": 42}

    async def mock_use_case() -> dict[str, object]:
        return result_value

    task_id = "test_task_1"

    with caplog.at_level(logging.INFO):
        await APScheduler._use_case_task_wrapper(mock_use_case, task_id)

    assert f"Starting scheduled task: {task_id}" in caplog.text
    assert f"Task '{task_id}' completed successfully" in caplog.text


async def test_wrapper_handles_exception(caplog: LogCaptureFixture) -> None:
    """Test that wrapper catches and logs exceptions."""
    error_msg = "Database connection failed"

    async def failing_use_case() -> None:
        raise ValueError(error_msg)

    task_id = "failing_task"

    with caplog.at_level(logging.ERROR):
        await APScheduler._use_case_task_wrapper(failing_use_case, task_id)

    assert f"Task '{task_id}' failed" in caplog.text
    assert error_msg in caplog.text


async def test_wrapper_does_not_propagate_exception() -> None:
    async def failing_use_case() -> None:
        raise RuntimeError("Critical error")

    await APScheduler._use_case_task_wrapper(failing_use_case, "test_task")


def test_schedule_use_case_adds_job(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
    caplog: LogCaptureFixture,
) -> None:
    task_id = "test_scheduled_task"
    trigger = IntervalTrigger(seconds=60)

    with caplog.at_level(logging.INFO):
        scheduler.schedule_use_case(
            use_case_factory=async_use_case, task_id=task_id, trigger=trigger
        )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == task_id
    assert jobs[0].name == task_id

    assert "Scheduled use case task" in caplog.text


def test_schedule_use_case_replaces_existing_job(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    task_id = "replaceable_task"
    trigger1 = IntervalTrigger(seconds=30)
    trigger2 = IntervalTrigger(seconds=60)

    scheduler.schedule_use_case(async_use_case, task_id, trigger1)

    scheduler.schedule_use_case(async_use_case, task_id, trigger2)
    jobs = scheduler._scheduler.get_jobs()
    assert any(job.id == task_id for job in jobs)


def test_schedule_every_n_days_creates_correct_trigger(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
    caplog: LogCaptureFixture,
) -> None:
    task_id = "daily_task"
    days = 2
    run_time = time(12, 30)

    with caplog.at_level(logging.INFO):
        scheduler.schedule_every_n_days(
            use_case_factory=async_use_case,
            days=days,
            task_id=task_id,
            run_time=run_time,
        )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == task_id

    assert f"Scheduled task to run every {days} days at {run_time}" in caplog.text


def test_schedule_every_n_days_default_midnight(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    task_id = "midnight_task"
    days = 1

    scheduler.schedule_every_n_days(
        use_case_factory=async_use_case, days=days, task_id=task_id
    )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1


@patch("src.adapters.inbound.scheduler.apscheduler.datetime")
def test_schedule_every_n_days_next_run_calculation_future(
    mock_datetime: Mock,
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    now = datetime(2024, 1, 15, 10, 0, 0)
    mock_datetime.now.return_value = now
    mock_datetime.combine = datetime.combine

    run_time = time(14, 0)

    scheduler.schedule_every_n_days(
        use_case_factory=async_use_case,
        days=1,
        task_id="future_task",
        run_time=run_time,
    )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1


@patch("src.adapters.inbound.scheduler.apscheduler.datetime")
def test_schedule_every_n_days_next_run_calculation_past(
    mock_datetime: Mock,
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    now = datetime(2024, 1, 15, 15, 0, 0)
    mock_datetime.now.return_value = now
    mock_datetime.combine = datetime.combine

    run_time = time(10, 0)

    scheduler.schedule_every_n_days(
        use_case_factory=async_use_case,
        days=1,
        task_id="past_task",
        run_time=run_time,
    )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1


def test_schedule_every_n_seconds_creates_job(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
    caplog: LogCaptureFixture,
) -> None:
    task_id = "frequent_task"
    seconds = 30

    with caplog.at_level(logging.INFO):
        scheduler.schedule_every_n_seconds(
            use_case_factory=async_use_case, seconds=seconds, task_id=task_id
        )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == task_id

    assert f"Scheduled task to run every {seconds} seconds" in caplog.text


def test_schedule_every_n_seconds_with_different_intervals(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    scheduler.schedule_every_n_seconds(async_use_case, 10, "task_10s")
    scheduler.schedule_every_n_seconds(async_use_case, 60, "task_60s")
    scheduler.schedule_every_n_seconds(async_use_case, 300, "task_300s")

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 3

    job_ids = {job.id for job in jobs}
    assert job_ids == {"task_10s", "task_60s", "task_300s"}


def test_add_job_with_custom_function(
    scheduler: APScheduler, caplog: LogCaptureFixture
) -> None:
    def custom_func() -> str:
        return "custom result"

    trigger = IntervalTrigger(seconds=120)
    task_id = "custom_job"

    with caplog.at_level(logging.INFO):
        scheduler.add_job(func=custom_func, trigger=trigger, task_id=task_id)

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == task_id

    assert f"Added custom job: {task_id}" in caplog.text


def test_add_job_with_kwargs(scheduler: APScheduler) -> None:
    def custom_func(arg1: int, arg2: int) -> int:
        return arg1 + arg2

    trigger = IntervalTrigger(seconds=60)
    task_id = "job_with_args"

    scheduler.add_job(func=custom_func, trigger=trigger, task_id=task_id, args=[5, 10])

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == task_id


def test_add_job_replaces_existing(scheduler: APScheduler) -> None:
    def func1() -> int:
        return 1

    def func2() -> int:
        return 2

    trigger = IntervalTrigger(seconds=60)
    task_id = "replaceable_custom_job"

    scheduler.add_job(func1, trigger, task_id)
    scheduler.add_job(func2, trigger, task_id)

    jobs = scheduler._scheduler.get_jobs()
    assert any(job.id == task_id for job in jobs)


async def test_start_starts_scheduler(
    scheduler: APScheduler, caplog: LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        scheduler.start()

    assert scheduler._scheduler.running
    assert "Scheduler started" in caplog.text

    scheduler.shutdown()


async def test_shutdown_stops_scheduler(
    scheduler: APScheduler, caplog: LogCaptureFixture
) -> None:
    scheduler.start()
    assert scheduler._scheduler.running

    with caplog.at_level(logging.INFO):
        scheduler.shutdown()

    assert "Scheduler stopped" in caplog.text


async def test_shutdown_waits_for_jobs(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    scheduler.schedule_every_n_seconds(async_use_case, 1, "test_task")
    scheduler.start()

    await asyncio.sleep(0.1)

    scheduler.shutdown()


def test_get_jobs_returns_empty_list(scheduler: APScheduler) -> None:
    jobs = scheduler.get_jobs()
    assert jobs == []


def test_get_jobs_returns_all_jobs(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    scheduler.schedule_every_n_seconds(async_use_case, 10, "task1")
    scheduler.schedule_every_n_seconds(async_use_case, 20, "task2")
    scheduler.schedule_every_n_seconds(async_use_case, 30, "task3")

    jobs = scheduler.get_jobs()
    assert len(jobs) == 3

    job_ids = {job.id for job in jobs}
    assert job_ids == {"task1", "task2", "task3"}


def test_get_jobs_after_removing_job(
    scheduler: APScheduler,
    async_use_case: Callable[[], Coroutine[Any, Any, dict[str, str]]],
) -> None:
    scheduler.schedule_every_n_seconds(async_use_case, 10, "task1")
    scheduler.schedule_every_n_seconds(async_use_case, 20, "task2")

    # Remove one job
    scheduler._scheduler.remove_job("task1")

    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "task2"


async def test_scheduled_task_execution(
    scheduler: APScheduler, caplog: LogCaptureFixture
) -> None:
    execution_count = {"count": 0}

    async def counting_use_case() -> dict[str, int]:
        execution_count["count"] += 1
        return {"executed": execution_count["count"]}

    scheduler.schedule_every_n_seconds(counting_use_case, 1, "counting_task")

    with caplog.at_level(logging.INFO):
        scheduler.start()

        await asyncio.sleep(1.5)

        scheduler.shutdown()

    assert execution_count["count"] >= 1
    assert "Starting scheduled task: counting_task" in caplog.text
    assert "Task 'counting_task' completed successfully" in caplog.text


async def test_multiple_tasks_execute_independently(scheduler: APScheduler) -> None:
    results = {"task1": 0, "task2": 0}

    async def task1_use_case() -> str:
        results["task1"] += 1
        return "task1"

    async def task2_use_case() -> str:
        results["task2"] += 1
        return "task2"

    scheduler.schedule_every_n_seconds(task1_use_case, 1, "task1")
    scheduler.schedule_every_n_seconds(task2_use_case, 1, "task2")

    scheduler.start()
    await asyncio.sleep(1.5)
    scheduler.shutdown()

    assert results["task1"] >= 1
    assert results["task2"] >= 1


async def test_failing_task_does_not_stop_scheduler(
    scheduler: APScheduler, caplog: LogCaptureFixture
) -> None:
    success_count = {"count": 0}

    async def failing_use_case() -> None:
        raise ValueError("Task failed")

    async def success_use_case() -> str:
        success_count["count"] += 1
        return "success"

    scheduler.schedule_every_n_seconds(failing_use_case, 1, "failing_task")
    scheduler.schedule_every_n_seconds(success_use_case, 1, "success_task")

    with caplog.at_level(logging.ERROR):
        scheduler.start()
        await asyncio.sleep(1.5)
        scheduler.shutdown()

    assert "Task 'failing_task' failed" in caplog.text

    assert success_count["count"] >= 1

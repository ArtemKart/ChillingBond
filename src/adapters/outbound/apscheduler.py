import logging
from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class APSchedulerAdapter:
    """
    Adapter for APScheduler.
    Implements Scheduler port using APScheduler library.
    """

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def schedule_daily(
        self, task: Callable[[], Awaitable[None]], hour: int, minute: int, task_id: str
    ) -> None:
        """
        Schedule a task to run daily at specified time.

        Args:
            task: Async function to execute
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
            task_id: Unique identifier for the task
        """
        async def safe_task_wrapper():
            """Wrapper to handle exceptions and logging."""
            logger = logging.getLogger(__name__)
            try:
                await task()
                logger.info(f"Task '{task_id}' completed successfully")
            except Exception as e:
                logger.error(
                    f"Task '{task_id}' failed",
                    exc_info=True,
                    extra={"error": str(e)}
                )

        self._scheduler.add_job(
            safe_task_wrapper,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=task_id,
            name=task_id,
            replace_existing=True,
        )

        logger.info(
            "Scheduled daily task",
            extra={"task_id": task_id, "hour": hour, "minute": minute},
        )

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        """Stop the scheduler gracefully."""
        self._scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

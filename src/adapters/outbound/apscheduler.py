import logging
from typing import Awaitable, Callable

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.domain.ports.services.scheduler import Scheduler

logger = logging.getLogger(__name__)


class APScheduler(Scheduler):
    """
    Adapter for APScheduler.
    Implements Scheduler port using APScheduler library.
    """

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def schedule_daily_http(
            self,
            url: str,
            method: str,
            hour: int,
            minute: int,
            task_id: str
    ) -> None:
        """
        Schedule an HTTP request to run daily at specified time.

        Args:
            url: URL to call
            method: HTTP method (GET, POST, etc.)
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
            task_id: Unique identifier for the task
        """

        async def http_task():
            """Make HTTP request to the endpoint."""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(method, url)
                    response.raise_for_status()
                    logger.info(
                        f"Task '{task_id}' completed successfully",
                        extra={"status_code": response.status_code}
                    )
            except Exception as e:
                logger.error(
                    f"Task '{task_id}' failed",
                    exc_info=True,
                    extra={"error": str(e)}
                )

        self._scheduler.add_job(
            http_task,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=task_id,
            name=task_id,
            replace_existing=True
        )

        logger.info(
            "Scheduled daily HTTP task",
            extra={
                "task_id": task_id,
                "url": url,
                "hour": hour,
                "minute": minute
            }
        )

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        """Stop the scheduler gracefully."""
        self._scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

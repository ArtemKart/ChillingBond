import logging

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class APScheduler:
    """
    Scheduler using APScheduler's AsyncIOScheduler for managing scheduled tasks.
    """

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    @staticmethod
    async def _http_task(url: str, task_id: str) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(
                    f"HTTP task completed with status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(
                f"Task '{task_id}' failed", exc_info=True, extra={"error": str(e)}
            )

    def schedule_every_n_days_http(
        self,
        url: str,
        days: int,
        task_id: str,
        hour: int = 0,
        minute: int = 0,
    ) -> None:
        """Schedule an HTTP request to run every N days at specified time."""
        from apscheduler.triggers.interval import IntervalTrigger
        from datetime import time, datetime, timedelta

        now = datetime.now()
        next_run = datetime.combine(now.date(), time(hour, minute))
        if next_run <= now:
            next_run += timedelta(days=1)

        self._scheduler.add_job(
            self._http_task,
            trigger=IntervalTrigger(days=days, start_date=next_run),
            args=[url, task_id],
            id=task_id,
            name=task_id,
            replace_existing=True,
        )

        logger.info(
            f"Scheduled HTTP task every {days} days",
            extra={
                "task_id": task_id,
                "url": url,
                "days": days,
                "next_run": next_run.isoformat(),
            },
        )

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        """Stop the scheduler gracefully."""
        self._scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

import logging
from datetime import datetime, time, timedelta
from typing import Any, Callable, Coroutine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.adapters.inbound.scheduler.scheduler_container import SchedulerContainer

logger = logging.getLogger(__name__)


class APScheduler:

    def __init__(self, container: SchedulerContainer):
        self._scheduler = AsyncIOScheduler()
        self._container = container

    @staticmethod
    async def _use_case_task_wrapper(
        use_case_factory: Callable[[], Coroutine[Any, Any, Any]],
        task_id: str,
    ) -> None:
        try:
            logger.info(f"Starting scheduled task: {task_id}")

            result = await use_case_factory()

            logger.info(
                f"Task '{task_id}' completed successfully",
                extra={"task_id": task_id, "result": str(result)},
            )

        except Exception as e:
            logger.error(
                f"Task '{task_id}' failed",
                exc_info=True,
                extra={"task_id": task_id, "error": str(e)},
            )

    def schedule_use_case(
        self,
        use_case_factory: Callable[[], Coroutine[Any, Any, Any]],
        task_id: str,
        trigger: IntervalTrigger,
    ) -> None:
        self._scheduler.add_job(
            self._use_case_task_wrapper,
            trigger=trigger,
            args=[use_case_factory, task_id],
            id=task_id,
            name=task_id,
            replace_existing=True,
        )

        logger.info(
            "Scheduled use case task",
            extra={
                "task_id": task_id,
                "trigger": str(trigger),
            },
        )

    def schedule_every_n_days(
        self,
        use_case_factory: Callable[[], Coroutine[Any, Any, Any]],
        days: int,
        task_id: str,
        run_time: time = time(0, 0),
    ) -> None:
        now = datetime.now()
        next_run = datetime.combine(now.date(), run_time)

        if next_run <= now:
            next_run += timedelta(days=1)

        trigger = IntervalTrigger(
            days=days,
            start_date=next_run,
        )

        self.schedule_use_case(
            use_case_factory=use_case_factory,
            task_id=task_id,
            trigger=trigger,
        )

        logger.info(
            f"Scheduled task to run every {days} days at {run_time}",
            extra={
                "task_id": task_id,
                "days": days,
                "run_time": str(run_time),
                "next_run": next_run.isoformat(),
            },
        )

    def schedule_every_n_seconds(
        self,
        use_case_factory: Callable[[], Coroutine[Any, Any, Any]],
        seconds: int,
        task_id: str,
    ) -> None:
        trigger = IntervalTrigger(seconds=seconds)

        self.schedule_use_case(
            use_case_factory=use_case_factory,
            task_id=task_id,
            trigger=trigger,
        )

        logger.info(
            f"Scheduled task to run every {seconds} seconds",
            extra={"task_id": task_id, "seconds": seconds},
        )

    def add_job(
        self,
        func: Callable,
        trigger: Any,
        task_id: str,
        **kwargs,
    ) -> None:
        self._scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            name=task_id,
            replace_existing=True,
            **kwargs,
        )
        logger.info(f"Added custom job: {task_id}")

    def start(self) -> None:
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        self._scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

    def get_jobs(self) -> list:
        return self._scheduler.get_jobs()

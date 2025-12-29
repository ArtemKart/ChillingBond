import asyncio
import logging
import signal
import sys
from datetime import datetime

from src.adapters.inbound.scheduler.apscheduler import APScheduler
from src.adapters.inbound.scheduler.scheduler_container import SchedulerContainer
from src.setup_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def handle_shutdown(signum, frame):
    logger.info("Received shutdown signal, stopping scheduler...")
    sys.exit(0)


def health_check_task():
    logger.info(
        f"❤️ Scheduler is ALIVE! Current time: {datetime.utcnow().isoformat()} UTC"
    )


async def main():
    async def update_reference_rates_task():
        """Execute update reference rates use case."""
        use_case = await container.get_update_reference_rate_use_case()
        result = await use_case.execute()
        logger.info(
            f"Reference rate update completed: {result.message}",
            extra={
                "success": result.success,
                "rate_changed": result.rate_changed,
                "rate_value": str(result.rate_value) if result.rate_value else None,
                "effective_date": (
                    result.effective_date.isoformat() if result.effective_date else None
                ),
            },
        )
        return result

    logger.info("=" * 60)
    logger.info("Starting Scheduler Worker")
    logger.info("=" * 60)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    container = SchedulerContainer()
    logger.info("✅ DI Container initialized")

    scheduler = APScheduler(container=container)

    scheduler.schedule_every_n_days(
        use_case_factory=update_reference_rates_task,
        days=3,
        task_id="nbp_reference_rate_updater",
    )

    scheduler.add_job(
        func=health_check_task,
        trigger="interval",
        task_id="health_check",
        hours=1,
    )

    scheduler.start()
    logger.info("✅ Scheduler started successfully")
    logger.info(f"Active jobs: {len(scheduler.get_jobs())}")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.id}: next run at {job.next_run_time}")

    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        await container.cleanup()
        logger.info("✅ Scheduler stopped gracefully")


if __name__ == "__main__":
    asyncio.run(main())

from typing import Callable, Awaitable
from abc import ABC

class Scheduler(ABC):
    """
    Port for task scheduler.
    Allows scheduling periodic tasks.
    """
    
    def schedule_daily(
        self,
        task: Callable[[], Awaitable[None]],
        hour: int,
        minute: int,
        task_id: str
    ) -> None:
        """
        Schedule a task to run daily at specified time.
        
        Args:
            task: Async function to execute
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
            task_id: Unique identifier for the task
        """
        ...
    
    def start(self) -> None:
        """Start the scheduler."""
        ...
    
    def shutdown(self) -> None:
        """Stop the scheduler gracefully."""
        ...

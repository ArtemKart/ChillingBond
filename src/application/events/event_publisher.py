import logging
from typing import Type, Callable, TypeVar, Coroutine, Any

from src.domain.events import DomainEvent


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=DomainEvent)


class EventPublisher:
    def __init__(self) -> None:
        self._handlers: dict[Type[DomainEvent], list[Callable]] = {}

    def subscribe(
        self, event_type: Type[T], handler: Callable[[T], Coroutine[Any, Any, None]]
    ) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

        handlers = [h.__self__.__class__.__name__ for h in self._handlers[event_type]]  # type: ignore[attr-defined]
        logger.debug(
            "Event handler subscribed",
            extra={
                "event_type": event_type.__name__,
                "handlers": handlers,
            },
        )

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        if event_type not in self._handlers:
            logger.debug(
                "No handlers for event",
                extra={"event_type": event_type.__name__},
            )
            return

        for handler in self._handlers[event_type]:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    "Event handler failed",
                    extra={
                        "event_type": event_type.__name__,
                        "handler": handler.__name__,
                        "error": str(e),
                    },
                )

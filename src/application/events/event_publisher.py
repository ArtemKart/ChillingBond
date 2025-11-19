from typing import Type, Callable

from src.domain.events import DomainEvent


class EventPublisher:
    def __init__(self) -> None:
        self._handlers: dict[Type[DomainEvent], list[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

        # TODO: place logger here
        # logger.debug(
        #     "Event handler subscribed",
        #     event_type=event_type.__name__,
        #     handler=handler.__name__,
        # )
    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        if event_type not in self._handlers:
            # TODO: place logger here
            # logger.debug(
            #     "No handlers for event",
            #     event_type=event_type.__name__,
            # )
            return

        # logger.info(
        #     "Publishing event",
        #     event_type=event_type.__name__,
        #     handlers_count=len(self._handlers[event_type]),
        # )

        for handler in self._handlers[event_type]:
            try:
                await handler(event)
                # logger.debug(
                #     "Event handler executed successfully",
                #     event_type=event_type.__name__,
                #     handler=handler.__name__,
                # )
            except Exception as _:
                pass
                # logger.error(
                #     "Event handler failed",
                #     event_type=event_type.__name__,
                #     handler=handler.__name__,
                #     error=str(e),
                #     exc_info=True,
                # )

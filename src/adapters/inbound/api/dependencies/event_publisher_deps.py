from typing import Annotated

from fastapi import Request, Depends

from src.application.events.event_publisher import EventPublisher


def get_event_publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]

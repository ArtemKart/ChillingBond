from datetime import datetime, timezone
from uuid import uuid4, UUID

import pytest
from unittest.mock import AsyncMock

from _pytest.logging import LogCaptureFixture

from src.application.events.event_publisher import EventPublisher
from src.domain.events import DomainEvent


class UserCreatedEvent(DomainEvent):
    def __init__(self, user_id: UUID, email: str):
        self.user_id = user_id
        self.email = email
        self.occurred_at = datetime.now(timezone.utc)


class OrderPlacedEvent(DomainEvent):
    def __init__(self, order_id: UUID, amount: float):
        self.order_id = order_id
        self.amount = amount
        self.occurred_at = datetime.now(timezone.utc)


@pytest.fixture
def publisher():
    return EventPublisher()


@pytest.fixture
def mock_handler():
    return AsyncMock()


async def test_subscribe_single_handler(publisher: EventPublisher, mock_handler: AsyncMock) -> None:
    publisher.subscribe(UserCreatedEvent, mock_handler)

    assert UserCreatedEvent in publisher._handlers
    assert mock_handler in publisher._handlers[UserCreatedEvent]


async def test_subscribe_multiple_handlers_same_event(publisher: EventPublisher) -> None:
    handler1 = AsyncMock()
    handler2 = AsyncMock()

    publisher.subscribe(UserCreatedEvent, handler1)
    publisher.subscribe(UserCreatedEvent, handler2)

    assert len(publisher._handlers[UserCreatedEvent]) == 2
    assert handler1 in publisher._handlers[UserCreatedEvent]
    assert handler2 in publisher._handlers[UserCreatedEvent]


async def test_subscribe_multiple_event_types(publisher: EventPublisher) -> None:
    handler1 = AsyncMock()
    handler2 = AsyncMock()

    publisher.subscribe(UserCreatedEvent, handler1)
    publisher.subscribe(OrderPlacedEvent, handler2)

    assert UserCreatedEvent in publisher._handlers
    assert OrderPlacedEvent in publisher._handlers
    assert handler1 in publisher._handlers[UserCreatedEvent]
    assert handler2 in publisher._handlers[OrderPlacedEvent]


async def test_publish_calls_handler(publisher: EventPublisher, mock_handler: AsyncMock) -> None:
    event = UserCreatedEvent(user_id=uuid4(), email="test@example.com")
    publisher.subscribe(UserCreatedEvent, mock_handler)

    await publisher.publish(event)

    mock_handler.assert_awaited_once_with(event)


async def test_publish_calls_multiple_handlers(publisher: EventPublisher) -> None:
    handler1 = AsyncMock()
    handler2 = AsyncMock()
    event = UserCreatedEvent(user_id=uuid4(), email="test@example.com")

    publisher.subscribe(UserCreatedEvent, handler1)
    publisher.subscribe(UserCreatedEvent, handler2)

    await publisher.publish(event)

    handler1.assert_awaited_once_with(event)
    handler2.assert_awaited_once_with(event)


async def test_publish_handler_exception_continues_execution(publisher: EventPublisher) -> None:
    failing_handler = AsyncMock(side_effect=ValueError("Test error"))
    success_handler = AsyncMock()
    event = UserCreatedEvent(user_id=uuid4(), email="test@example.com")

    publisher.subscribe(UserCreatedEvent, failing_handler)
    publisher.subscribe(UserCreatedEvent, success_handler)

    await publisher.publish(event)

    failing_handler.assert_awaited_once()
    success_handler.assert_awaited_once()


async def test_publish_all_empty_list(publisher: EventPublisher) -> None:
    await publisher.publish_all([])


async def test_publish_all_multiple_events(publisher: EventPublisher) -> None:
    handler1 = AsyncMock()
    handler2 = AsyncMock()

    event1 = UserCreatedEvent(user_id=uuid4(), email="test1@example.com")
    event2 = UserCreatedEvent(user_id=uuid4(), email="test2@example.com")

    publisher.subscribe(UserCreatedEvent, handler1)
    publisher.subscribe(UserCreatedEvent, handler2)

    await publisher.publish_all([event1, event2])

    assert handler1.await_count == 2
    assert handler2.await_count == 2
    handler1.assert_any_await(event1)
    handler2.assert_any_await(event2)


async def test_publish_all_different_event_types(publisher: EventPublisher) -> None:
    user_handler = AsyncMock()
    order_handler = AsyncMock()

    user_event = UserCreatedEvent(user_id=uuid4(), email="test@example.com")
    order_event = OrderPlacedEvent(order_id=uuid4(), amount=50.0)

    publisher.subscribe(UserCreatedEvent, user_handler)
    publisher.subscribe(OrderPlacedEvent, order_handler)

    await publisher.publish_all([user_event, order_event])

    user_handler.assert_awaited_once_with(user_event)
    order_handler.assert_awaited_once_with(order_event)


async def test_publish_all_handler_exception_continues(publisher: EventPublisher, caplog: LogCaptureFixture) -> None:
    failing_handler = AsyncMock(side_effect=ValueError("First event failed"))
    success_handler = AsyncMock()

    event1 = UserCreatedEvent(user_id=uuid4(), email="test1@example.com")
    event2 = UserCreatedEvent(user_id=uuid4(), email="test2@example.com")

    publisher.subscribe(UserCreatedEvent, failing_handler)
    publisher.subscribe(UserCreatedEvent, success_handler)

    await publisher.publish_all([event1, event2])

    assert failing_handler.await_count == 2
    assert success_handler.await_count == 2
    assert caplog.text.count("Event handler failed") == 2


async def test_publish_only_calls_handlers_for_specific_event_type(publisher: EventPublisher) -> None:
    user_handler = AsyncMock()
    order_handler = AsyncMock()

    user_event = UserCreatedEvent(user_id=uuid4(), email="test@example.com")

    publisher.subscribe(UserCreatedEvent, user_handler)
    publisher.subscribe(OrderPlacedEvent, order_handler)

    await publisher.publish(user_event)

    user_handler.assert_awaited_once()
    order_handler.assert_not_awaited()


async def test_event_inheritance(publisher: EventPublisher) -> None:
    class BaseEvent(DomainEvent):
        pass

    class DerivedEvent(BaseEvent):
        pass

    base_handler = AsyncMock()
    derived_handler = AsyncMock()

    publisher.subscribe(BaseEvent, base_handler)
    publisher.subscribe(DerivedEvent, derived_handler)

    derived_event = DerivedEvent(occurred_at=datetime.now(timezone.utc))

    await publisher.publish(derived_event)

    derived_handler.assert_awaited_once()
    base_handler.assert_not_awaited()

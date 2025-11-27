from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio

from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.events.bondholder_events import BondHolderDeletedEvent
from src.domain.exceptions import ValidationError


@pytest_asyncio.fixture
def local_bondholder() -> BondHolderEntity:
    return BondHolderEntity(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=100,
        purchase_date=date.today(),
    )

async def test_bondholder_change_quantity_success(local_bondholder: BondHolderEntity) -> None:
    new_quantity = 300
    local_bondholder.change_quantity(new_quantity)
    assert local_bondholder.quantity == new_quantity

async def test_bondholder_change_quantity_type_error(local_bondholder: BondHolderEntity) -> None:
    with pytest.raises(ValidationError, match="Quantity must be an integer"):
        local_bondholder.change_quantity("one")  # type: ignore [arg-type]

async def test_bondholder_change_quantity_quantity_error(local_bondholder: BondHolderEntity) -> None:
    with pytest.raises(ValidationError, match="Quantity must be positive"):
        local_bondholder.change_quantity(-1)

async def test_bondholder_mark_as_deleted(
    local_bondholder: BondHolderEntity,
) -> None:
    user_email = "test_user_email@email.com"
    local_bondholder.mark_as_deleted(user_email=user_email)
    assert local_bondholder._events
    assert isinstance(local_bondholder._events[0], BondHolderDeletedEvent)
    assert local_bondholder.id == local_bondholder._events[0].bondholder_id
    assert local_bondholder.bond_id == local_bondholder._events[0].bond_id
    assert local_bondholder.user_id == local_bondholder._events[0].user_id
    assert user_email == local_bondholder._events[0].email


async def test_bondholder_collect_events(local_bondholder: BondHolderEntity) -> None:
    bh_event = BondHolderDeletedEvent(
        bondholder_id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        email="test_user_email@email.com",
        occurred_at=datetime.now(timezone.utc),
    )
    local_bondholder._events.append(bh_event)

    events = local_bondholder.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], BondHolderDeletedEvent)

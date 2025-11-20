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


async def test_bondholder_add_quantity_err(local_bondholder: BondHolderEntity) -> None:
    negative_quantity = -local_bondholder.quantity

    with pytest.raises(ValidationError, match="Amount must be positive"):
        local_bondholder.add_quantity(negative_quantity)

    assert local_bondholder.quantity != negative_quantity


async def test_bondholder_add_quantity_happy_path(
    local_bondholder: BondHolderEntity,
) -> None:
    before = local_bondholder.quantity
    amount = 44
    local_bondholder.add_quantity(amount=amount)
    assert local_bondholder.quantity == before + amount


@pytest.mark.parametrize(
    "quantity, amount, expected_result",
    [
        (100, 44, 56),
        (100, 101, 0),
    ],
    ids=["amount less than quantity", "amount greater than quantity"],
)
async def test_bondholder_reduce_quantity(
    local_bondholder: BondHolderEntity,
    quantity: int,
    amount: int,
    expected_result: int,
) -> None:
    local_bondholder.quantity = quantity
    local_bondholder.reduce_quantity(amount=amount)
    assert local_bondholder.quantity == expected_result


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

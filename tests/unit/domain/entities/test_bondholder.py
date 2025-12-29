from datetime import date, datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4, UUID

import pytest

from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.events.bondholder_events import BondHolderDeletedEvent
from src.domain.exceptions import ValidationError


@pytest.fixture
def local_bondholder() -> BondHolderEntity:
    return BondHolderEntity(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=100,
        purchase_date=date.today(),
    )


def test_bondholder_change_quantity_success(
    local_bondholder: BondHolderEntity,
) -> None:
    new_quantity = 300
    local_bondholder.change_quantity(new_quantity)
    assert local_bondholder.quantity == new_quantity


def test_bondholder_change_quantity_type_error(
    local_bondholder: BondHolderEntity,
) -> None:
    with pytest.raises(ValidationError, match="Quantity must be an integer"):
        local_bondholder.change_quantity("one")  # type: ignore [arg-type]


def test_bondholder_change_quantity_quantity_error(
    local_bondholder: BondHolderEntity,
) -> None:
    with pytest.raises(ValidationError, match="Quantity must be positive"):
        local_bondholder.change_quantity(-1)


def test_bondholder_mark_as_deleted(
    local_bondholder: BondHolderEntity,
) -> None:
    user_email = "test_user_email@email.com"
    local_bondholder.mark_as_deleted(user_email=user_email)

    assert local_bondholder._events

    event = local_bondholder._events[0]
    assert isinstance(event, BondHolderDeletedEvent)
    assert local_bondholder.id == event.bondholder_id
    assert local_bondholder.bond_id == event.bond_id
    assert local_bondholder.user_id == event.user_id
    assert user_email == event.email


def test_bondholder_collect_events(local_bondholder: BondHolderEntity) -> None:
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


def test_bondholder_create(
    local_bondholder: BondHolderEntity, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_validate = MagicMock()
    monkeypatch.setattr(BondHolderEntity, "validate", mock_validate)

    new_bh = BondHolderEntity.create(
        bond_id=local_bondholder.bond_id,
        user_id=local_bondholder.user_id,
        quantity=10,
        purchase_date=local_bondholder.purchase_date,
        last_update=local_bondholder.last_update,
    )

    assert new_bh.id is not None
    assert isinstance(new_bh.id, UUID)
    assert new_bh.id.version == 4
    assert new_bh.id != local_bondholder.id
    assert new_bh.bond_id == local_bondholder.bond_id
    assert new_bh.user_id == local_bondholder.user_id
    assert new_bh.purchase_date == local_bondholder.purchase_date
    assert new_bh.last_update == local_bondholder.last_update
    assert new_bh.quantity == 10

    mock_validate.assert_called_once()


def test_bondholder_validate(
    local_bondholder: BondHolderEntity, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_validate_quantity = MagicMock()
    monkeypatch.setattr(local_bondholder, "_validate_quantity", mock_validate_quantity)

    local_bondholder.validate()

    mock_validate_quantity.assert_called_once()


def test_validate_quantity_success(local_bondholder: BondHolderEntity) -> None:
    local_bondholder.quantity = 10
    local_bondholder._validate_quantity()


def test_validate_quantity_negative_quantity(local_bondholder: BondHolderEntity) -> None:
    local_bondholder.quantity = -10
    with pytest.raises(ValidationError, match="Quantity must be positive"):
        local_bondholder._validate_quantity()


def test_validate_quantity_zero_quantity(local_bondholder: BondHolderEntity) -> None:
    local_bondholder.quantity = 0
    with pytest.raises(ValidationError, match="Quantity must be positive"):
        local_bondholder._validate_quantity()

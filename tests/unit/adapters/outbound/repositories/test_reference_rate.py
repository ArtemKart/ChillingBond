from __future__ import annotations

import random
from datetime import timedelta, date
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.adapters.outbound.database.models import ReferenceRate as ReferenceRateModel
from src.adapters.outbound.repositories.reference_rate import (
    SQLAlchemyReferenceRateRepository,
)
from src.domain.entities.reference_rate import ReferenceRate as ReferenceRateEntity


@pytest.fixture
def repository(
    mock_session: AsyncMock,
) -> SQLAlchemyReferenceRateRepository:
    return SQLAlchemyReferenceRateRepository(mock_session)


@pytest.fixture
def mock_reference_rate_model(mock_reference_rate_entity: Mock) -> ReferenceRateModel:
    return ReferenceRateModel(
        id=uuid4(),
        value=mock_reference_rate_entity.value,
        start_date=mock_reference_rate_entity.start_date,
        end_date=mock_reference_rate_entity.end_date,
    )


def _get_random_date_between(start_date: date, end_date: date) -> date:
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, delta.seconds)
    return start_date + timedelta(days=random_days, seconds=random_seconds)


async def test_get_by_date_success(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
    mock_reference_rate_model: ReferenceRateModel,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_reference_rate_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_date(
        _get_random_date_between(
            mock_reference_rate_entity.start_date,
            mock_reference_rate_entity.end_date,
        )
    )

    assert result is not None
    assert isinstance(result, ReferenceRateEntity)
    assert result.value == mock_reference_rate_entity.value
    assert result.start_date == mock_reference_rate_entity.start_date
    assert result.end_date == mock_reference_rate_entity.end_date


async def test_get_by_date_not_found(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
    mock_reference_rate_model: ReferenceRateModel,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_date(
        _get_random_date_between(
            mock_reference_rate_entity.start_date,
            mock_reference_rate_entity.end_date,
        )
    )

    assert result is None


async def test_save_success(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
    mock_reference_rate_model: ReferenceRateModel,
) -> None:
    mock_session.refresh = AsyncMock(return_value=None)

    async def fake_refresh(model: ReferenceRateModel) -> None:
        model.id = mock_reference_rate_model.id
        model.value = mock_reference_rate_model.value
        model.start_date = mock_reference_rate_model.start_date
        model.end_date = mock_reference_rate_model.end_date

    mock_session.refresh.side_effect = fake_refresh

    result = await repository.save(mock_reference_rate_entity)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert isinstance(result, ReferenceRateEntity)
    assert result.value == mock_reference_rate_entity.value
    assert result.start_date == mock_reference_rate_entity.start_date
    assert result.end_date == mock_reference_rate_entity.end_date


async def test_save_integrity_error_raises_repository_error(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
) -> None:
    from sqlite3 import IntegrityError
    from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError

    mock_session.commit.side_effect = IntegrityError()

    with pytest.raises(
        SQLAlchemyRepositoryError, match="already exists or constraint violated"
    ):
        await repository.save(mock_reference_rate_entity)

    mock_session.rollback.assert_called_once()


async def test_save_sqlalchemy_error_raises_repository_error(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
) -> None:
    from sqlalchemy.exc import SQLAlchemyError
    from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError

    mock_session.commit.side_effect = SQLAlchemyError()

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to save ReferenceRate"):
        await repository.save(mock_reference_rate_entity)

    mock_session.rollback.assert_called_once()


async def test_get_latest_success(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
    mock_reference_rate_model: ReferenceRateModel,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_reference_rate_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_latest()

    mock_session.execute.assert_called_once()
    assert result is not None
    assert isinstance(result, ReferenceRateEntity)
    assert result.value == mock_reference_rate_entity.value
    assert result.start_date == mock_reference_rate_entity.start_date
    assert result.end_date == mock_reference_rate_entity.end_date


async def test_get_latest_not_found(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repository.get_latest()

    assert result is None


async def test_update_success(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
    mock_reference_rate_model: ReferenceRateModel,
) -> None:
    mock_session.get.return_value = mock_reference_rate_model

    result = await repository.update(mock_reference_rate_entity)

    mock_session.get.assert_called_once_with(
        ReferenceRateModel, mock_reference_rate_entity.id
    )
    mock_session.commit.assert_called_once()
    assert isinstance(result, ReferenceRateEntity)
    assert result.value == mock_reference_rate_entity.value
    assert result.start_date == mock_reference_rate_entity.start_date
    assert result.end_date == mock_reference_rate_entity.end_date


async def test_update_not_found_raises_not_found_error(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
) -> None:
    from src.domain.exceptions import NotFoundError

    mock_session.get.return_value = None

    with pytest.raises(NotFoundError, match="ReferenceRate not found"):
        await repository.update(mock_reference_rate_entity)

    mock_session.commit.assert_not_called()


async def test_get_by_date_with_open_ended_rate(
    mock_session: AsyncMock,
    repository: SQLAlchemyReferenceRateRepository,
    mock_reference_rate_entity: Mock,
) -> None:
    open_ended_model = ReferenceRateModel(
        id=uuid4(),
        value=mock_reference_rate_entity.value,
        start_date=date(2024, 1, 1),
        end_date=None,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = open_ended_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_date(date(2025, 6, 15))

    assert result is not None
    assert isinstance(result, ReferenceRateEntity)
    assert result.end_date is None

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

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from src.domain.entities.bond import Bond as BondEntity


@pytest.fixture
def bond_model(bond_entity_mock: Mock) -> BondModel:
    return BondModel(
        id=bond_entity_mock.id,
        series=bond_entity_mock.series,
        nominal_value=bond_entity_mock.nominal_value,
        maturity_period=bond_entity_mock.maturity_period,
        initial_interest_rate=bond_entity_mock.initial_interest_rate,
        first_interest_period=bond_entity_mock.first_interest_period,
        reference_rate_margin=bond_entity_mock.reference_rate_margin,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(mock_session)


async def test_get_one_success(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_model: BondModel,
    bond_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = bond_model
    result = await repository.get_one_or_none(bond_entity_mock.id)

    mock_session.get.assert_called_once_with(BondModel, bond_entity_mock.id)
    assert result is not None
    assert result.id == bond_entity_mock.id
    assert result.series == bond_entity_mock.series
    assert result.nominal_value == bond_entity_mock.nominal_value


async def test_get_one_not_found(
    repository: SQLAlchemyBondRepository, mock_session: AsyncMock
) -> None:
    bond_id = uuid4()
    mock_session.get.return_value = None

    result = await repository.get_one_or_none(bond_id)

    mock_session.get.assert_called_once_with(BondModel, bond_id)
    assert result is None


async def test_get_by_series_success(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_model: BondModel,
    bond_entity_mock: Mock,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = bond_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_series_or_none(bond_entity_mock.series)

    mock_session.execute.assert_called_once()
    assert result is not None
    assert result.series == bond_entity_mock.series
    assert result.id == bond_entity_mock.id


async def test_get_by_series_not_found(
    repository: SQLAlchemyBondRepository, mock_session: AsyncMock
) -> None:
    series = "non-existent"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_series_or_none(series)

    mock_session.execute.assert_called_once()
    assert result is None


async def test_write_success(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.write(bond_entity_mock)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bond_entity_mock.id
    assert result.series == bond_entity_mock.series


async def test_write_integrity_error(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = None
    mock_session.commit.side_effect = IntegrityError("", "", "")
    with pytest.raises(
        SQLAlchemyRepositoryError, match="Bond already exists or constraint violated"
    ):
        await repository.write(bond_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_write_sqlalchemy_error(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = None
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to save bond"):
        await repository.write(bond_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_update_success(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_entity_mock: Mock,
    bond_model: BondModel,
) -> None:
    mock_session.get.return_value = bond_model
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    bond_entity_mock.nominal_value = 200.0
    bond_entity_mock.initial_interest_rate = 5.0

    result = await repository.update(bond_entity_mock)

    mock_session.get.assert_called_once_with(BondModel, bond_entity_mock.id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bond_entity_mock.id


async def test_update_sqlalchemy_error(
    repository: SQLAlchemyBondRepository,
    mock_session: AsyncMock,
    bond_entity_mock: Mock,
) -> None:
    mock_session.get.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to update bond"):
        await repository.update(bond_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_delete_success(
    repository: SQLAlchemyBondRepository, mock_session: AsyncMock, bond_model: BondModel
) -> None:
    bond_id = uuid4()
    mock_session.get.return_value = bond_model
    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    await repository.delete(bond_id)

    mock_session.get.assert_called_once_with(BondModel, bond_id)
    mock_session.delete.assert_called_once_with(bond_model)
    mock_session.commit.assert_called_once()


async def test_delete_not_found(
    repository: SQLAlchemyBondRepository, mock_session: AsyncMock
) -> None:
    bond_id = uuid4()
    mock_session.get.return_value = None

    await repository.delete(bond_id)

    mock_session.get.assert_called_once_with(BondModel, bond_id)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


async def test_delete_sqlalchemy_error(
    repository: SQLAlchemyBondRepository, mock_session: AsyncMock
) -> None:
    bond_id = uuid4()
    mock_session.get.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to delete bond"):
        await repository.delete(bond_id)
    mock_session.rollback.assert_called_once()


def test_to_entity_conversion(
    repository: SQLAlchemyBondRepository, bond_model: BondModel
) -> None:
    result = repository._to_entity(bond_model)

    assert isinstance(result, BondEntity)
    assert result.id == bond_model.id
    assert result.series == bond_model.series
    assert result.nominal_value == bond_model.nominal_value
    assert result.maturity_period == bond_model.maturity_period
    assert result.initial_interest_rate == bond_model.initial_interest_rate
    assert result.first_interest_period == bond_model.first_interest_period
    assert result.reference_rate_margin == bond_model.reference_rate_margin


def test_to_model_conversion(
    repository: SQLAlchemyBondRepository, bond_entity_mock: Mock
) -> None:
    result = repository._to_model(bond_entity_mock)

    assert isinstance(result, BondModel)
    assert result.id == bond_entity_mock.id
    assert result.series == bond_entity_mock.series
    assert result.nominal_value == bond_entity_mock.nominal_value
    assert result.maturity_period == bond_entity_mock.maturity_period
    assert result.initial_interest_rate == bond_entity_mock.initial_interest_rate
    assert result.first_interest_period == bond_entity_mock.first_interest_period
    assert result.reference_rate_margin == bond_entity_mock.reference_rate_margin


def test_update_model(
    repository: SQLAlchemyBondRepository, bond_model: BondModel, bond_entity_mock: Mock
) -> None:
    new_entity = BondEntity(
        id=bond_entity_mock.id,
        series="ROR0000",
        nominal_value=Decimal("3000.0"),
        maturity_period=730,
        initial_interest_rate=Decimal("8.0"),
        first_interest_period=60,
        reference_rate_margin=Decimal("3.0"),
    )
    repository._update_model(bond_model, new_entity)

    assert bond_model.series == "ROR0000"
    assert bond_model.nominal_value == Decimal("3000.0")
    assert bond_model.maturity_period == 730
    assert bond_model.initial_interest_rate == Decimal("8.0")
    assert bond_model.first_interest_period == 60
    assert bond_model.reference_rate_margin == Decimal("3.0")

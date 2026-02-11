from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies.repo_deps import (
    BondHolderRepoDep,
    BondRepoDep,
)
from src.adapters.inbound.api.dependencies.service_deps import analytics_service
from src.application.use_cases.data.get_equity_history import GetEquityHistoryUseCase
from src.domain.services.analytics.analytics_service import AnalyticsService


def get_equity_history_use_case(
    bond_repo: BondRepoDep,
    bondholder_repo: BondHolderRepoDep,
    analytics_service: Annotated[AnalyticsService, Depends(analytics_service)],
) -> GetEquityHistoryUseCase:
    return GetEquityHistoryUseCase(
        bh_repo=bondholder_repo, bond_repo=bond_repo, service=analytics_service
    )

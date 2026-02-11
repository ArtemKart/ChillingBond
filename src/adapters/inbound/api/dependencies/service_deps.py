from src.adapters.inbound.api.dependencies.repo_deps import (
    BondHolderRepoDep,
    BondRepoDep,
)
from src.adapters.outbound.external_services.nbp.fetcher import NBPXMLFetcher
from src.adapters.outbound.external_services.nbp.nbp_data_provider import NBPDataProvider
from src.adapters.outbound.external_services.nbp.parser import NBPXMLParser
from src.domain.services.analytics.analytics_service import AnalyticsService
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


def bh_deletion_service(
    bh_repo: BondHolderRepoDep,
    bond_repo: BondRepoDep,
) -> BondHolderDeletionService:
    return BondHolderDeletionService(bondholder_repo=bh_repo, bond_repo=bond_repo)


def nbp_data_provider_dep() -> NBPDataProvider:
    return NBPDataProvider(
        fetcher=NBPXMLFetcher(),
        parser=NBPXMLParser(),
    )


def analytics_service() -> AnalyticsService:
    return AnalyticsService()

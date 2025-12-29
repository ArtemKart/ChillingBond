import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.config import Config, get_config
from src.adapters.outbound.database.engine import get_session
from src.adapters.outbound.external_services.nbp.fetcher import NBPXMLFetcher
from src.adapters.outbound.external_services.nbp.nbp_data_provider import (
    NBPDataProvider,
)
from src.adapters.outbound.external_services.nbp.parser import NBPXMLParser
from src.adapters.outbound.repositories.reference_rate import (
    SQLAlchemyReferenceRateRepository,
)
from src.application.use_cases.reference_rate.update import UpdateReferenceRateUseCase
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.domain.ports.services.reference_rate_provider import ReferenceRateProvider

logger = logging.getLogger(__name__)


class SchedulerContainer:

    def __init__(self) -> None:
        self._session: AsyncSession | None = None
        self._config: Config | None = None
        self._nbp_fetcher: NBPXMLFetcher | None = None
        self._nbp_parser: NBPXMLParser | None = None
        self._nbp_provider: NBPDataProvider | None = None

        logger.info("Scheduler DI Container initialized")

    def get_config(self) -> Config:
        if self._config is None:
            self._config = get_config()
        return self._config

    @staticmethod
    async def _get_session() -> AsyncSession:
        return await anext(get_session())

    def get_nbp_fetcher(self) -> NBPXMLFetcher:
        if self._nbp_fetcher is None:
            self._nbp_fetcher = NBPXMLFetcher(timeout=30, max_retries=3)
            logger.debug("Created NBPXMLFetcher instance")
        return self._nbp_fetcher

    def get_nbp_parser(self) -> NBPXMLParser:
        if self._nbp_parser is None:
            self._nbp_parser = NBPXMLParser()
            logger.debug("Created NBPXMLParser instance")
        return self._nbp_parser

    def get_nbp_provider(self) -> ReferenceRateProvider:
        if self._nbp_provider is None:
            fetcher = self.get_nbp_fetcher()
            parser = self.get_nbp_parser()
            self._nbp_provider = NBPDataProvider(fetcher=fetcher, parser=parser)
            logger.debug("Created NBPDataProvider instance")
        return self._nbp_provider

    @staticmethod
    def get_reference_rate_repository(session: AsyncSession) -> ReferenceRateRepository:
        return SQLAlchemyReferenceRateRepository(session=session)

    async def get_update_reference_rate_use_case(
        self,
    ) -> UpdateReferenceRateUseCase:
        repository = self.get_reference_rate_repository(await self._get_session())
        provider = self.get_nbp_provider()

        use_case = UpdateReferenceRateUseCase(
            reference_rate_repo=repository, rate_provider=provider
        )

        logger.debug("Created UpdateReferenceRateUseCase with all dependencies")
        return use_case

    async def cleanup(self) -> None:
        if self._nbp_fetcher:
            await self._nbp_fetcher.close()
            logger.info("Closed NBP fetcher HTTP client")

        logger.info("Scheduler DI Container cleaned up")

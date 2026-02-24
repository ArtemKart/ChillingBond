from datetime import date
from decimal import Decimal

from src.application.dto.data import EquityDTO
from src.application.dto.user import UserDTO
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.services.analytics.analytics_service import AnalyticsService


class GetEquityHistoryUseCase:
    def __init__(
        self,
        bh_repo: BondHolderRepository,
        bond_repo: BondRepository,
        service: AnalyticsService,
    ) -> None:
        self.bh_repo: BondHolderRepository = bh_repo
        self.bond_repo: BondRepository = bond_repo
        self.service: AnalyticsService = service

    async def execute(self, user: UserDTO) -> EquityDTO:
        bhs = await self.bh_repo.get_all(user_id=user.id)
        if not bhs:
            return self._to_dto(data=[])
        bonds_dict = await self.bond_repo.fetch_dict_from_bondholders(bondholders=bhs)
        bondholder_data = [(bh, bonds_dict[bh.bond_id].nominal_value) for bh in bhs]
        history_data = self.service.get_equity_history(bondholder_data=bondholder_data)
        return self._to_dto(data=history_data)

    @staticmethod
    def _to_dto(data: list[tuple[date, Decimal]]) -> EquityDTO:
        return EquityDTO(data=data)

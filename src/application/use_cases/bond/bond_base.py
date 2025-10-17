from src.application.dto.bond import BondDTO
from src.domain.entities.bond import Bond


class BondBaseUseCase:
    @staticmethod
    async def to_dto(bond: Bond) -> BondDTO:
        return BondDTO(
            id=bond.id,
            buy_date=bond.buy_date,
            nominal_value=bond.nominal_value,
            series=bond.series,
            maturity_period=bond.maturity_period,
            initial_interest_rate=bond.initial_interest_rate,
            first_interest_period=bond.first_interest_period,
            reference_rate_margin=bond.reference_rate_margin,
            last_update=bond.last_update,
            user_id=bond.user_id,
        )

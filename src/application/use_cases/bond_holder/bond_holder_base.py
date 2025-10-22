from src.application.dto.bond_holder import BondHolderDTO
from src.domain.entities.bond import Bond
from src.domain.entities.bond_holder import BondHolder


class BondHolderBaseUseCase:
    @staticmethod
    async def to_dto(bond_holder: BondHolder, bond: Bond) -> BondHolderDTO:
        return BondHolderDTO(
            id=bond_holder.id,
            user_id=bond_holder.user_id,
            quantity=bond_holder.quantity,
            purchase_date=bond_holder.purchase_date,
            bond_id=bond_holder.bond_id,
            last_update=bond_holder.last_update,
            series=bond.series,
            nominal_value=bond.nominal_value,
            maturity_period=bond.maturity_period,
            initial_interest_rate=bond.initial_interest_rate,
            first_interest_period=bond.first_interest_period,
            reference_rate_margin=bond.reference_rate_margin,
        )

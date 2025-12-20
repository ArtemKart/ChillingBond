from src.application.dto.bondholder import BondHolderDTO
from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder


class BondHolderBaseUseCase:
    @staticmethod
    def to_dto(bondholder: BondHolder, bond: Bond) -> BondHolderDTO:
        return BondHolderDTO(
            id=bondholder.id,
            user_id=bondholder.user_id,
            quantity=bondholder.quantity,
            purchase_date=bondholder.purchase_date,
            bond_id=bondholder.bond_id,
            last_update=bondholder.last_update,
            series=bond.series,
            nominal_value=bond.nominal_value,
            maturity_period=bond.maturity_period,
            initial_interest_rate=bond.initial_interest_rate,
            first_interest_period=bond.first_interest_period,
            reference_rate_margin=bond.reference_rate_margin,
        )

from src.application.dto.bond import BondCreateDTO
from src.application.dto.bondholder import BondHolderCreateDTO, BondHolderDTO
from src.application.use_cases.bondholder.base import BondHolderBaseUseCase
from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.entities.bond import Bond as BondEntity


class BondHolderCreateUseCase(BondHolderBaseUseCase):
    """
    Create BondHolder. Connect BondHolder to the existing Bond
    if Bond is not exist, otherwise create Bond.
    """

    def __init__(
        self, bond_repo: BondRepository, bondholder_repo: BondHolderRepository
    ) -> None:
        self.bond_repo: BondRepository = bond_repo
        self.bondholder_repo: BondHolderRepository = bondholder_repo

    async def execute(
        self, bh_dto: BondHolderCreateDTO, b_dto: BondCreateDTO
    ) -> BondHolderDTO:
        bond = await self.bond_repo.get_by_series(b_dto.series)
        if bond:
            new_bh = BondHolderEntity.create(
                bond_id=bond.id,
                user_id=bh_dto.user_id,
                quantity=bh_dto.quantity,
                purchase_date=bh_dto.purchase_date,
            )
            new_bh = await self.bondholder_repo.write(new_bh)
            if not new_bh:
                raise
            return self.to_dto(bondholder=new_bh, bond=bond)

        new_bond = BondEntity.create(
            series=b_dto.series,
            nominal_value=b_dto.nominal_value,
            maturity_period=b_dto.maturity_period,
            initial_interest_rate=b_dto.initial_interest_rate,
            first_interest_period=b_dto.first_interest_period,
            reference_rate_margin=b_dto.reference_rate_margin,
        )
        new_bond = await self.bond_repo.write(new_bond)
        if not new_bond:
            raise
        new_bh = BondHolderEntity.create(
            bond_id=new_bond.id,
            user_id=bh_dto.user_id,
            quantity=bh_dto.quantity,
            purchase_date=bh_dto.purchase_date,
        )
        new_bh = await self.bondholder_repo.write(new_bh)
        return self.to_dto(bondholder=new_bh, bond=new_bond)

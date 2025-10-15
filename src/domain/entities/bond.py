from dataclasses import dataclass

from src.domain.exceptions import BondDomainError


@dataclass
class Bond:
    """ Represents the bond

    Args:
        id (int): Bond identifier.
        nominal_value (float): Nominal value of a single bond unit.
        series (str): Identifier or code representing the bond series.
        maturity_period (int): Total lifetime of the bond, typically expressed
            in months.
        initial_interest_rate (float): Interest rate applied during the initial
            period of the bond.
        first_interest_period (int): Duration of the initial interest rate period,
            typically expressed in months.
        reference_rate_margin (float): Additional percentage added to the reference rate (spread).
    """

    id: int
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float


    def _check_initial_period_duration(self) -> None:
        if self.first_interest_period > self.maturity_period:
            error_msg = "First Interest period cannot be larger that bond maturity period"
            raise BondDomainError(error_msg)

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Bond:
    """Represents the bondholder

    Args:
        id (UUID): Bond identifier.
        nominal_value (float): Nominal value of a single bondholder unit.
        series (str): Identifier or code representing the bondholder series.
        maturity_period (int): Total lifetime of the bondholder, typically expressed
            in months.
        initial_interest_rate (float): Interest rate applied during the initial
            period of the bondholder.
        first_interest_period (int): Duration of the initial interest rate period,
            typically expressed in months.
        reference_rate_margin (float): Additional percentage added to the reference rate (spread).
    """

    id: UUID
    series: str
    nominal_value: float
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float

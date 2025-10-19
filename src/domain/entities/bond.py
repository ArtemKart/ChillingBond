from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Bond:
    """Represents the bond

    Args:
        id (UUID): Bond identifier.
        buy_date (datetime): Bond buy date.
        nominal_value (float): Nominal value of a single bond unit.
        series (str): Identifier or code representing the bond series.
        maturity_period (int): Total lifetime of the bond, typically expressed
            in months.
        initial_interest_rate (float): Interest rate applied during the initial
            period of the bond.
        first_interest_period (int): Duration of the initial interest rate period,
            typically expressed in months.
        reference_rate_margin (float): Additional percentage added to the reference rate (spread).
        user_id (UUID): User identifier.
        last_update (datetime): Bond last update time.
    """

    id: UUID
    buy_date: datetime
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float
    user_id: UUID
    last_update: datetime | None = None

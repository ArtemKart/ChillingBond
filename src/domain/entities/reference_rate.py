from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReferenceRate:
    """ Represents the reference rate
    Args:
        id (int): Reference rate identifier.
        value (float): Reference rate value.
        start_date (datetime): Date from which the reference rate becomes effective.
        end_date (datetime): Date until which the reference rate is valid.
            Can be None if it is still in effect.
    """
    id: int
    value: float
    start_date: datetime
    end_date: datetime

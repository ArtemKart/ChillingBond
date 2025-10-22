from pydantic import BaseModel


class BondUpdateRequest(BaseModel):
    nominal_value: float | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: float | None = None
    first_interest_period: int | None = None
    reference_rate_margin: float | None = None


class BondUpdateResponse(BaseModel):
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float

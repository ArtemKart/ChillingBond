from pydantic import BaseModel, Field


class BondBase(BaseModel):
    series: str = Field(..., min_length=1, description="Bond series")
    nominal_value: float = Field(..., gt=0, description="Nominal value")
    maturity_period: int = Field(..., gt=0, description="Maturity period in months")
    initial_interest_rate: float = Field(..., gt=0, description="Initial interest rate")

    first_interest_period: int = Field(..., gt=0, description="First interest period")
    reference_rate_margin: float = Field(..., description="Reference rate margin")


class BondUpdateRequest(BaseModel):
    series: str | None = Field(None, min_length=1)
    nominal_value: float | None = Field(None, gt=0)
    maturity_period: int | None = Field(None, gt=0)
    initial_interest_rate: float | None = Field(None, gt=0)
    first_interest_period: int | None = Field(None, gt=0)
    reference_rate_margin: float | None = Field(None)


class BondUpdateResponse(BondBase):
    pass


class EmptyBondUpdateResponse(BaseModel):
    pass

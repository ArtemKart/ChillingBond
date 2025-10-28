from pydantic import BaseModel, Field, model_validator


class BondBase(BaseModel):
    series: str = Field(..., min_length=1, description="Bond series")
    nominal_value: float = Field(..., gt=0, description="Nominal value")
    maturity_period: int = Field(..., gt=0, description="Maturity period in months")
    initial_interest_rate: float = Field(..., gt=0, description="Initial interest rate")
    first_interest_period: int = Field(..., gt=0, description="First interest period")
    reference_rate_margin: float = Field(...,description="Reference rate margin")


class BondUpdateRequest(BaseModel):
    series: str | None = Field(None, min_length=1)
    nominal_value: float | None = Field(None, gt=0)
    maturity_period: int | None = Field(None, gt=0)
    initial_interest_rate: float | None = Field(None, gt=0)
    first_interest_period: int | None = Field(None, gt=0)
    reference_rate_margin: float | None = Field(None)

    @model_validator(mode="after")
    def check_any_field_present(self):
        if not any(
                value is not None for value in self.model_dump().values()
        ):
            raise ValueError("At least one field must be provided for update.")
        return self


class BondUpdateResponse(BondBase):
    pass

from pydantic import BaseModel, model_validator


class BondUpdateRequest(BaseModel):
    nominal_value: float | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: float | None = None
    first_interest_period: int | None = None
    reference_rate_margin: float | None = None

    @model_validator(mode="after")
    def check_any_field_present(self):
        if not any(
                value is not None for value in self.model_dump().values()
        ):
            raise ValueError("At least one field must be provided for update.")
        return self


class BondUpdateResponse(BaseModel):
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float

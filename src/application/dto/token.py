from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenDTO:
    token: str
    type: str

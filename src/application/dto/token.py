from dataclasses import dataclass


@dataclass
class TokenDTO:
    token: str
    type: str

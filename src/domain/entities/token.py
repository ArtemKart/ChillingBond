from dataclasses import dataclass


@dataclass
class Token:
    """Represents token

    Args:
        token (str): Token itself.
        type (str): Token type.
    """

    token: str
    type: str

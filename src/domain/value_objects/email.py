from dataclasses import dataclass
import re
from typing import override


@dataclass(frozen=True)
class Email:
    """Email value object with built-in normalization and validation"""

    value: str

    def __init__(self, value: str) -> None:
        normalized = value.strip().lower()
        if not self._is_valid(normalized):
            raise ValueError("Invalid email format")

        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        res = re.match(pattern, email)
        return True if res else False

    @override
    def __str__(self) -> str:
        return self.value

from src.domain.exceptions import ValidationError


class PasswordPolicy:
    MIN_LENGTH = 8

    @staticmethod
    async def validate(password: str) -> None:
        if len(password) < PasswordPolicy.MIN_LENGTH:
            raise ValidationError("Password too short")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Must contain digit")

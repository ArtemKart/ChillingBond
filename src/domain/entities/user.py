from dataclasses import dataclass


@dataclass
class User:
    """ Represents the user

    Args:
        id (int): User identifier.
        email (str): User email.
        password (str): User password.
        name (str, None): User first name.
    """

    id: int
    email: str
    password: str
    name: str | None

from dataclasses import dataclass

from app.core.config import settings
from app.security.passwords import hash_password, password_needs_rehash, verify_password


@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int = settings.password_min_length
    max_length: int = settings.password_max_length

    def validate(self, password: str) -> None:
        if not isinstance(password, str):
            raise TypeError("Invalid password.")
        if len(password) < self.min_length:
            raise ValueError("Password is too short.")
        if len(password) > self.max_length:
            raise ValueError("Password is too long.")
        if not any(character.isalpha() for character in password):
            raise ValueError("Password must contain at least one letter.")
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must contain at least one number.")


class PasswordService:
    def __init__(self, policy: PasswordPolicy | None = None) -> None:
        self.policy = policy or PasswordPolicy()

    def hash(self, password: str) -> str:
        self.policy.validate(password)
        return hash_password(password)

    def verify(self, password: str, password_hash: str) -> bool:
        if not password or len(password) > self.policy.max_length:
            return False
        return verify_password(password, password_hash)

    def needs_rehash(self, password_hash: str) -> bool:
        return password_needs_rehash(password_hash)

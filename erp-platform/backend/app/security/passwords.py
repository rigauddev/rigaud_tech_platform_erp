import bcrypt

from app.core.config import settings

BCRYPT_PREFIX = "$2b$"
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    password_bytes = _password_bytes(password)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS, prefix=b"2b")
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            _password_bytes(plain_password),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def password_needs_rehash(hashed_password: str) -> bool:
    return not hashed_password.startswith(f"{BCRYPT_PREFIX}{BCRYPT_ROUNDS}$")


def _password_bytes(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > settings.password_max_length:
        msg = "Password exceeds the configured maximum length."
        raise ValueError(msg)
    return password_bytes

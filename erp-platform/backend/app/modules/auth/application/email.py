import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    normalized_email = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized_email):
        raise ValueError("Invalid email format.")
    return normalized_email


def normalize_tenant(tenant: str) -> str:
    normalized_tenant = tenant.strip().lower()
    if not normalized_tenant:
        raise ValueError("Invalid tenant.")
    return normalized_tenant

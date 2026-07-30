from dataclasses import dataclass


@dataclass(frozen=True)
class MfaChallenge:
    subject: str
    method: str
    reference: str

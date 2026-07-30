from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

    @property
    def is_debug(self) -> bool:
        return self in {self.LOCAL, self.DEVELOPMENT, self.TEST}

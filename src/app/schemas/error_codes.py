from enum import Enum, auto
from typing import Any, List


class AutoNameEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(  # type: ignore
        name: str, start: int, count: int, last_values: List[Any]  # noqa: N805
    ) -> str:
        return name.upper()


class CustomServiceErrorCodes(AutoNameEnum):
    """
    General Service Error Codes
    """

    # General API errors
    INVALID_HEADERS = auto()
    UNAUTHORIZED = auto()
    RESOURCE_FORBIDDEN = auto()
    VALIDATION_ERROR = auto()
    RESOURCE_NOT_FOUND = auto()

    # Users-specific errors
    USER_DOES_NOT_EXIST = auto()

    # Internal Server Error
    INTERNAL_SERVER_ERROR = auto()

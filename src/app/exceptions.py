from typing import Any

from starlette import status
from starlette.exceptions import HTTPException

from app.schemas.error_codes import CustomServiceErrorCodes


class CustomServiceException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: CustomServiceErrorCodes,
        details: Any = None,
    ) -> None:
        self.error_code = error_code
        self.details = details
        super().__init__(status_code, message)

    def __str__(self) -> str:
        return self.detail


class UserDoesNotExistError(CustomServiceException):
    def __init__(self, message: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code=CustomServiceErrorCodes.USER_DOES_NOT_EXIST,
        )

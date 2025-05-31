from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette.responses import JSONResponse

from .exceptions import CustomServiceException
from .schemas import CustomServiceError, CustomServiceErrorCodes, ErrorResponse


def handle_custome_service_exception(
    _: Request, exception: CustomServiceException
) -> JSONResponse:
    """Handle errors specific to the service"""
    payload = ErrorResponse(
        error=CustomServiceError(
            code=exception.error_code, message=exception.detail, details=exception.details
        )
    )
    return JSONResponse(
        status_code=exception.status_code, content=jsonable_encoder(payload)
    )


def handle_validation_exception(_: Request, exception: ValidationError) -> JSONResponse:
    """Handle ValidationErrors raised by FastAPI"""
    payload = ErrorResponse(
        error=CustomServiceError(
            code=CustomServiceErrorCodes.VALIDATION_ERROR,
            message=str(exception),
            details=exception.errors(),
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(payload),
    )


def arbitrary_exception_handler(_: Request, exception: Exception) -> JSONResponse:
    """
    According to people experience in StackOverflow
    common exception handlers work only if app.debug is False
    """
    payload = ErrorResponse(
        error=CustomServiceError(
            code=CustomServiceErrorCodes.INTERNAL_SERVER_ERROR,
            message="Internal Server Error",
            details=None,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(payload),
    )

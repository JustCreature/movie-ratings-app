import typing as t

import structlog
import uvicorn  # type: ignore
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.middleware import Middleware

from app.api.api import api_router
from app.api.openapi import OpenApiDocumentation
from app.context import ContextMiddleware
from app.exception_handlers import (
    arbitrary_exception_handler,
    handle_custome_service_exception,
    handle_validation_exception,
)
from app.exceptions import CustomServiceException
from app.schemas.error_response import ErrorResponse
from app.settings import settings

# just a comment

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

# Define error responses that we may return
responses: t.Dict[t.Union[str, int], t.Dict[str, t.Any]] = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    404: {"model": ErrorResponse, "description": "Not Found"},
    409: {"model": ErrorResponse, "description": "Conflict"},
    422: {"model": ErrorResponse, "description": "Validation Error"},
}


def create_app():

    app = FastAPI(
        title="movie-rating-app",
        middleware=[Middleware(ContextMiddleware)],
        openapi_url="/docs/openapi.json",
        docs_url="/docs/",
        redoc_url="/docs/redocs/",
        responses=responses,
        debug=settings.DEBUG,
    )

    app.add_exception_handler(CustomServiceException, handle_custome_service_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(ValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, arbitrary_exception_handler)

    app.openapi = OpenApiDocumentation(app).custom_openapi  # type: ignore

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            path=request.scope.get("path", ""),
            method=request.scope.get("method", ""),
            query_string=request.scope.get("query_string", "").decode(),
            client=request.scope.get("client", ("-",))[0],
            url=str(request.url),
        )
        response: Response = await call_next(request)
        return response

    app.include_router(api_router, prefix="/api")

    # @app.on_event("startup")
    # async def startup():
    #     async with engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    #     log.info("database_initialized")

    return app


def main():
    # https://www.uvicorn.org/settings/
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        workers=1,
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload,
        log_level=settings.uvicorn.log_level,
    )


if __name__ == "__main__":
    main()

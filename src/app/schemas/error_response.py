from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from .error_codes import CustomServiceErrorCodes


class CustomServiceError(BaseModel):
    code: CustomServiceErrorCodes
    message: str
    details: Optional[Any]


class ErrorResponse(BaseModel):
    error: CustomServiceError

    model_config = SettingsConfigDict(
        json_encoders={datetime: lambda dt: dt.replace(tzinfo=timezone.utc).isoformat()}
    )

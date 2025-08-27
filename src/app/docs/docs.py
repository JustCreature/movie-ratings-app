import os
from pathlib import Path
from typing import Any

import chevron

from app.schemas.error_codes import CustomServiceErrorCodes

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"

permission_descriptions: dict[str, str] = {
    # map[PermissionName]PermissionDescription
}


def get_endpoint_description(
    title: str,
    description: str | None = None,
    # permissions: Optional[List[UserPermissionRequest]] = None,  # should be a permission reqeust to permify
    error_codes: dict[CustomServiceErrorCodes, str] | None = None,
) -> Any:
    # permissions_var = [{"name": v.action} for v in permissions] if permissions else []
    permissions_var: list = []
    custom_errors_var = (
        [{"code": k, "description": v} for k, v in error_codes.items()]
        if error_codes
        else []
    )

    vars = {
        "title": title,
        "description": description,
        "permissions": permissions_var,
        "has_custom_errors": len(custom_errors_var) > 0,
        "custom_errors": custom_errors_var,
    }

    # Render app description
    with open(templates_path / "endpoint_description.mustache", "r") as f:
        return chevron.render(f, vars)


common_error_code_descriptions: dict[CustomServiceErrorCodes, str] = {
    CustomServiceErrorCodes.DEPENDENCY_CLIENT_ERROR: (
        "HTTP error calling a dependency API service, dependency might be unreachable."
    ),
    CustomServiceErrorCodes.EXTERNAL_SERVICE_ERROR: (
        "An external API returned errors, there may be a problem with your request."
    ),
    CustomServiceErrorCodes.VALIDATION_ERROR: "Request schema validation failed.",
}


def get_app_description() -> Any:
    permissions = [
        {"name": k, "description": v} for k, v in permission_descriptions.items()
    ]
    error_codes = [
        {"code": k, "description": v} for k, v in common_error_code_descriptions.items()
    ]

    # Render app description
    with open(templates_path / "app_description.mustache", "r") as f:
        return chevron.render(f, {"permissions": permissions, "error_codes": error_codes})

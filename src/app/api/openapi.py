from typing import Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class OpenApiDocumentation:
    def __init__(self, app: FastAPI):
        self.app = app

    def custom_openapi(self) -> Dict:
        if self.app.openapi_schema:
            return self.app.openapi_schema

        openapi_schema = get_openapi(
            title=self.app.title,
            version=self.app.version,
            description=self.app.description,
            routes=self.app.routes,
            tags=self.app.openapi_tags,
        )

        openapi_schema["servers"] = [
            {
                "url": "http://localhost:{port}",
                "description": "local",
                "variables": {"port": {"default": 8054}},
            },
        ]
        self.app.openapi_schema = openapi_schema

        return self.app.openapi_schema

import pydantic


class UvicornSettings(pydantic.BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "info"
    reload: bool = False

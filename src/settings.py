from os import getenv
from typing import Optional, Any

from pydantic import BaseModel


class Settings(BaseModel):
    https_proxy: Optional[str]

    DISCORD_TOKEN: str
    DISCORD_HISTORY_MAX_LEN: int = 10

    GEMINI_TOKEN: str
    GEMINI_MODEL: str = "gemini-2.0-flash"


def parse_settings() -> Settings:
    schema = Settings.model_json_schema()
    values: dict[str, Any] = dict()
    for key in schema["properties"]:
        val = getenv(key)
        if val:
            values[key] = val

    return Settings.model_validate(values)


if __name__ == "__main__":
    settings = parse_settings()
    print(settings.model_dump())

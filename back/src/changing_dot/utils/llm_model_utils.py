import os

from pydantic.v1.types import SecretStr


def get_mistral_api_key() -> SecretStr:
    return SecretStr(os.getenv("MISTRAL_API_KEY") or "")

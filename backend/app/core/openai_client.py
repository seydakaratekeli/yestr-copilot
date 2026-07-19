from functools import lru_cache

from openai import OpenAI

from app.core.config import settings


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY tanımlanmamış."
        )

    return OpenAI(
        api_key=settings.openai_api_key
    )
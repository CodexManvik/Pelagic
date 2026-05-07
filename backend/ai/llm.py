from functools import lru_cache

from langchain_groq import ChatGroq

from core.config import get_settings


@lru_cache(maxsize=1)
def build_chat_model() -> ChatGroq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("Missing GROQ_API_KEY.")

    return ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=settings.groq_temperature,
        max_retries=settings.groq_max_retries,
        timeout=settings.groq_timeout_seconds,
    )

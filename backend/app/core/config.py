from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YeS-TR Copilot API"
    environment: str = "development"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    frontend_url: str

    storage_bucket: str

    max_pdf_size_mb: int = 25
    max_pdf_page_count: int = 50
    max_files_per_request: int = 10

    chunk_size_characters: int = 1800
    chunk_overlap_characters: int = 250
    minimum_chunk_characters: int = 80

    ocr_enabled: bool = True
    ocr_languages: str = "tur+eng"
    ocr_dpi: int = 300
    ocr_minimum_native_characters: int = 30
    ocr_minimum_result_characters: int = 20
    tessdata_path: str | None = None

    embedding_enabled: bool = True
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_dimension: int = 384
    embedding_batch_size: int = 16

    minimum_embedding_characters: int = 80
    minimum_embedding_words: int = 8
    minimum_text_quality_score: float = 0.55

    openai_api_key: str | None = None

    llm_enabled: bool = True
    llm_model: str = "gpt-5-mini"

    rag_search_limit: int = 6
    rag_minimum_similarity: float = 0.40
    rag_max_context_characters: int = 12_000

    rag_minimum_source_count: int = 1
    rag_max_quote_characters: int = 500

    conversation_context_message_limit: int = 6
    conversation_context_character_limit: int = 6000

    question_resolution_enabled: bool = True
    question_resolution_model: str = "gpt-5-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def max_pdf_size_bytes(self) -> int:
        return self.max_pdf_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings(**{})


settings = get_settings()

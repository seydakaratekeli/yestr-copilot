from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YeS-TR Copilot API"
    environment: str = "development"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    frontend_url: str = "http://localhost:3000"

    storage_bucket: str = "project-documents"

    max_pdf_size_mb: int = 25
    max_pdf_page_count: int = 50
    max_files_per_request: int = 10

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
    return Settings()


settings = get_settings()
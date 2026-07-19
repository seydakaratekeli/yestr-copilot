"""
Test ortamı için conftest.

Supabase bağlantı bilgileri `.env` dosyasından okunmak yerine
sahte değerlerle çevre değişkeni olarak ayarlanır.
Bu sayede testler gerçek Supabase bağlantısına ihtiyaç duymaz.
"""

import os
from unittest.mock import patch

import pytest


# Settings modülü import edilmeden ÖNCE çevre değişkenlerini set et.
# pydantic-settings @lru_cache kullandığı için modül ilk kez yüklendiğinde
# değerleri okur; bu yüzden conftest'te en üste koyuyoruz.
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "fake-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("STORAGE_BUCKET", "project-documents")
os.environ.setdefault("LLM_ENABLED", "false")


@pytest.fixture(autouse=True)
def mock_document_background_processing():
    with patch(
        "app.api.routes.documents.process_document",
        return_value=None,
    ):
        yield

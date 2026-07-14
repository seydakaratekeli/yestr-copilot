"""
Test ortamı için conftest.

Supabase bağlantı bilgileri `.env` dosyasından okunmak yerine
sahte değerlerle çevre değişkeni olarak ayarlanır.
Bu sayede testler gerçek Supabase bağlantısına ihtiyaç duymaz.
"""

import os

import pytest


# Settings modülü import edilmeden ÖNCE çevre değişkenlerini set et.
# pydantic-settings @lru_cache kullandığı için modül ilk kez yüklendiğinde
# değerleri okur; bu yüzden conftest'te en üste koyuyoruz.
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "fake-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")

from dotenv import load_dotenv
from supabase import create_client
import os

import pytest


if os.getenv("RUN_SUPABASE_SMOKE_TESTS") != "true":
    pytest.skip(
        "Canlı Supabase smoke testi devre dışı.",
        allow_module_level=True,
    )

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL") or "",
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "",
)

response = client.table("organizations").select("*").execute()

print("Bağlantı başarılı!")
print(response.data)

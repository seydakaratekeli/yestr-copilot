from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL") or "",
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "",
)

response = client.table("organizations").select("*").execute()

print("Bağlantı başarılı!")
print(response.data)
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)

response = client.table("organizations").select("*").execute()

print("Bağlantı başarılı!")
print(response.data)
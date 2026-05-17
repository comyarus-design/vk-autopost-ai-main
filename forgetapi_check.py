import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FORGETAPI_API_KEY")
base_url = os.getenv("FORGETAPI_BASE_URL", "https://api.forgetapi.ru/v1")

resp = httpx.get(
    f"{base_url}/models",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=30,
)

print("STATUS:", resp.status_code)
print(resp.text)
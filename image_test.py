import os
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("FORGETAPI_API_KEY")
base_url = os.getenv("FORGETAPI_BASE_URL", "https://api.forgetapi.ru/v1")
model = os.getenv("FORGETAPI_IMAGE_MODEL", "nano-banana")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

response = client.images.generate(
    model=model,
    prompt="Фотореалистичный робот-пылесос убирает современную светлую гостиную, дневной свет, аккуратный интерьер",
    size="1024x1024",
    n=1
)

item = response.data[0]

if getattr(item, "b64_json", None):
    img_bytes = base64.b64decode(item.b64_json)
    with open("test_robot.png", "wb") as f:
        f.write(img_bytes)
    print("Готово: test_robot.png")
elif getattr(item, "url", None):
    img = requests.get(item.url, timeout=120)
    img.raise_for_status()
    with open("test_robot.png", "wb") as f:
        f.write(img.content)
    print("Готово: test_robot.png")
else:
    print(response)
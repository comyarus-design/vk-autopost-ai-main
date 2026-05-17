import os
import base64
from datetime import datetime

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_image(prompt: str, output_dir: str = "content/images") -> str:
    api_key = os.getenv("FORGETAPI_API_KEY")
    base_url = os.getenv("FORGETAPI_BASE_URL", "https://api.forgetapi.ru/v1")
    model = os.getenv("FORGETAPI_IMAGE_MODEL", "nano-banana")

    if not api_key:
        raise ValueError("Не найден FORGETAPI_API_KEY в .env")

    os.makedirs(output_dir, exist_ok=True)

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024",
        n=1
    )

    item = response.data[0]
    filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(output_dir, filename)

    if getattr(item, "b64_json", None):
        img_bytes = base64.b64decode(item.b64_json)
        with open(file_path, "wb") as f:
            f.write(img_bytes)
    elif getattr(item, "url", None):
        img = requests.get(item.url, timeout=120)
        img.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(img.content)
    else:
        raise RuntimeError("API не вернул ни url, ни b64_json")

    return file_path


if __name__ == "__main__":
    prompt = "Фотореалистичный робот-пылесос убирает современную светлую гостиную, дневной свет, аккуратный интерьер"
    path = generate_image(prompt)
    print(f"Готово: {path}")
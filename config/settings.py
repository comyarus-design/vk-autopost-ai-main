import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True, encoding="utf-8")

VK_GROUP_TOKEN = (os.getenv("VK_GROUP_TOKEN") or "").strip()
VK_GROUP_ID = (os.getenv("VK_GROUP_ID") or "").strip()
VK_API_VERSION = (os.getenv("VK_API_VERSION") or "5.199").strip()
BASE_URL = (os.getenv("BASE_URL") or "https://example.com").strip()
CHECK_INTERVAL_SECONDS = int((os.getenv("CHECK_INTERVAL_SECONDS") or "60").strip())

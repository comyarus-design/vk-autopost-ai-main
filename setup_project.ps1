$ErrorActionPreference = "Stop"

$root = "C:\Users\Карташов Ярослав\vk-autopost-ai"

if (-not (Test-Path $root)) {
    throw "Project folder not found: $root"
}

Set-Location $root

$nested = Join-Path $root "vk-autopost-ai"
if (Test-Path $nested) {
    Remove-Item $nested -Recurse -Force
}

$dirs = @(
    "app",
    "config",
    "content",
    "content\images",
    "content\pages",
    "content\published",
    "data",
    "logs"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $root $dir) | Out-Null
}

$files = @{
    ".gitignore" = @'
.env
venv/
.venv/
__pycache__/
*.pyc
logs/
data/
content/images/
content/pages/
content/published/
'@

    ".env.example" = @'
VK_GROUP_TOKEN=your_vk_group_token_here
VK_GROUP_ID=your_group_id_here
VK_API_VERSION=5.199
BASE_URL=https://example.com
CHECK_INTERVAL_SECONDS=60
'@

    "requirements.txt" = @'
requests
APScheduler
Jinja2
python-dotenv
'@

    "README.md" = @'
# vk-autopost-ai

Автопостинг в сообщество VK с очередью, планировщиком и AI-подготовкой контента.
'@

    "config\settings.py" = @'
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN", "")
VK_GROUP_ID = os.getenv("VK_GROUP_ID", "")
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")
BASE_URL = os.getenv("BASE_URL", "https://example.com")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
'@

    "app\__init__.py" = @'
'@

    "app\db.py" = @'
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "posts.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            link_url TEXT NOT NULL,
            image_path TEXT,
            page_path TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            publish_at TEXT NOT NULL,
            vk_post_id TEXT,
            last_error TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
    conn.close()
'@

    "app\queue_service.py" = @'
from typing import List, Optional
from app.db import get_connection


def create_post(title: str, message: str, link_url: str, publish_at: str,
                image_path: Optional[str] = None, page_path: Optional[str] = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO posts (title, message, link_url, image_path, page_path, publish_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, message, link_url, image_path, page_path, publish_at),
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()
    return post_id


def get_pending_posts(limit: int = 10) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM posts
        WHERE status = 'pending'
        ORDER BY publish_at ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def mark_post_posted(post_id: int, vk_post_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE posts
        SET status = 'posted',
            vk_post_id = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (vk_post_id, post_id),
    )
    conn.commit()
    conn.close()


def mark_post_failed(post_id: int, error_message: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE posts
        SET status = 'failed',
            last_error = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (error_message, post_id),
    )
    conn.commit()
    conn.close()
'@

    "run.py" = @'
from app.db import init_db


def main():
    init_db()
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
'@
}

foreach ($relativePath in $files.Keys) {
    $fullPath = Join-Path $root $relativePath
    $parent = Split-Path $fullPath -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    Set-Content -Path $fullPath -Value $files[$relativePath] -Encoding UTF8
}

Write-Host "Project scaffold created successfully." -ForegroundColor Green
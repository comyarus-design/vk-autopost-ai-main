from typing import List, Optional
from app.db import get_connection


def create_post(
    title: str,
    message: str,
    link_url: str,
    publish_at: str,
    image_path: Optional[str] = None,
    page_path: Optional[str] = None
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO posts (title, message, link_url, image_path, page_path, publish_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """,
        (title, message, link_url, image_path, page_path, publish_at),
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()
    return post_id


def get_due_pending_posts(limit: int = 10) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM posts
        WHERE status = 'pending'
          AND datetime(publish_at) <= datetime('now', 'localtime')
        ORDER BY datetime(publish_at) ASC
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
        (str(vk_post_id), post_id),
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
        (error_message[:1000], post_id),
    )
    conn.commit()
    conn.close()


def list_posts(limit: int = 20) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM posts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
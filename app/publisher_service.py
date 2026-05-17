import logging

from app.db import get_connection
from app.vk_api import post_to_wall

logger = logging.getLogger(__name__)


def publish_due_posts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, message, link_url, image_path, status, publish_at, vk_post_id
        FROM posts
        ORDER BY id ASC
        """
    )
    all_posts = cur.fetchall()

    print("DEBUG_DB_ALL_POSTS_COUNT=", len(all_posts))
    for row in all_posts:
        print(
            "DEBUG_DB_POST",
            {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "publish_at": row["publish_at"],
                "vk_post_id": row["vk_post_id"],
            },
        )

    cur.execute(
        """
        SELECT id, title, message, link_url, image_path, status, publish_at
        FROM posts
        WHERE status = 'pending'
        ORDER BY id ASC
        """
    )
    posts = cur.fetchall()

    print("DEBUG_PENDING_POSTS_COUNT=", len(posts))

    processed = 0

    for row in posts:
        local_id = row["id"]
        title = row["title"]
        message = row["message"]
        link_url = row["link_url"]
        image_path = row["image_path"]
        status = row["status"]
        publish_at = row["publish_at"]

        print(
            "DEBUG_TRY_POST",
            {
                "id": local_id,
                "title": title,
                "status": status,
                "publish_at": publish_at,
                "image_path": image_path,
                "link_url": link_url,
            },
        )

        try:
            response = post_to_wall(
                message=message,
                link_url=link_url,
                image_path=image_path,
            )

            print("DEBUG_VK_RESPONSE=", response)

            vk_post_id = response["post_id"]

            cur.execute(
                """
                UPDATE posts
                SET status = 'posted',
                    vk_post_id = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (str(vk_post_id), local_id),
            )
            conn.commit()

            processed += 1
            print(f"POSTED: local_id={local_id} vk_post_id={vk_post_id}")

        except Exception as e:
            error_text = str(e)

            cur.execute(
                """
                UPDATE posts
                SET status = 'failed',
                    last_error = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (error_text, local_id),
            )
            conn.commit()

            print(f"FAILED: local_id={local_id} error={error_text}")

    conn.close()
    logger.info(f"publish_due_posts finished, processed={processed}")
    print("DEBUG_PROCESSED_COUNT=", processed)
    return processed
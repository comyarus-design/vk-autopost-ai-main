import logging

from app.db import get_connection
from app.vk_api import post_to_wall

logger = logging.getLogger(__name__)


def publish_due_posts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, message, link_url, image_path
        FROM posts
        WHERE status = 'pending'
          AND publish_at <= datetime('now', 'localtime')
        ORDER BY publish_at ASC
        """
    )

    posts = cur.fetchall()
    processed = 0

    for row in posts:
        local_id = row["id"]
        message = row["message"]
        link_url = row["link_url"]
        image_path = row["image_path"]

        try:
            print(
                f"DEBUG_POST local_id={local_id} "
                f"image_path={image_path} link_url={link_url}"
            )

            response = post_to_wall(
                message=message,
                link_url=link_url,
                image_path=image_path,
            )

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
    return processed
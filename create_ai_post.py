import json
from datetime import datetime, timedelta
from pathlib import Path

from app.db import init_db
from app.image_generator import generate_image
from app.page_generator import render_post_page
from app.queue_service import create_post

TOPICS_FILE = Path("content/topics.json")
PUBLISH_DELAY_MINUTES = 1


def load_topics_data() -> dict:
    if not TOPICS_FILE.exists():
        raise FileNotFoundError("Не найден файл content/topics.json")
    return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))


def save_topics_data(data: dict) -> None:
    TOPICS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_next_topic(data: dict) -> tuple[dict, int]:
    topics = data.get("topics", [])
    if not topics:
        raise ValueError("Список topics пустой")

    current_index = data.get("current_index", 0)
    if current_index >= len(topics):
        current_index = 0

    topic = topics[current_index]
    next_index = current_index + 1
    if next_index >= len(topics):
        next_index = 0

    return topic, next_index


def main():
    init_db()

    data = load_topics_data()
    topic, next_index = get_next_topic(data)

    title = topic["title"]
    description = topic["description"]
    message = topic["message"]
    image_prompt = topic["image_prompt"]
    body_html = topic["body_html"]

    image_path = generate_image(image_prompt)

    page_data = render_post_page(
        title=title,
        description=description,
        body_html=body_html,
        image_rel_path=image_path,
    )

    publish_time = (
        datetime.now() + timedelta(minutes=PUBLISH_DELAY_MINUTES)
    ).strftime("%Y-%m-%d %H:%M:%S")

    post_id = create_post(
        title=title,
        message=message,
        link_url=page_data["page_url"],
        publish_at=publish_time,
        image_path=image_path,
        page_path=page_data["page_path"],
    )

    data["current_index"] = next_index
    save_topics_data(data)

    print({
        "created_post_id": post_id,
        "used_topic": title,
        "next_topic_index": next_index,
        "publish_at": publish_time,
        "image_path": image_path,
        "page_path": page_data["page_path"],
        "page_url": page_data["page_url"],
    })


if __name__ == "__main__":
    main()
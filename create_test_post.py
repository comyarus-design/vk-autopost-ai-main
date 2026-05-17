from datetime import datetime, timedelta
from app.db import init_db
from app.queue_service import create_post
from app.image_generator import generate_image


def main():
    init_db()

    publish_time = (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")

    image_prompt = "Фотореалистичный робот-пылесос убирает современную светлую гостиную, дневной свет, аккуратный интерьер"
    image_path = generate_image(image_prompt)

    post_id = create_post(
        title="Тест фото",
        message="Это тестовый пост с картинкой, сгенерированной через ForgetAPI и добавленной в очередь автопостинга.",
        link_url="https://comyarus-design.github.io/vk-autopost-ai/content/pages/5-idey-dlya-avtomatizatsii-postinga-v-vk.html",
        publish_at=publish_time,
        image_path=image_path,
    )

    print({
        "created_post_id": post_id,
        "publish_at": publish_time,
        "image_path": image_path
    })


if __name__ == "__main__":
    main()
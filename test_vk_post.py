from datetime import datetime
from app.vk_api import post_text_to_wall


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        "Тестовый пост из системы vk-autopost-ai\n\n"
        f"Время: {now}\n"
        "Если этот пост опубликован, значит базовая интеграция с VK API работает."
    )

    result = post_text_to_wall(message)
    print(result)


if __name__ == "__main__":
    main()

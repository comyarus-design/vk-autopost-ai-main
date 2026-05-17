import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_post_content(topic: str) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("TEXT_MODEL", "openai/gpt-4o-mini")

    if not api_key:
        raise ValueError("Не найден OPENROUTER_API_KEY в .env")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    prompt = f"""
Ты пишешь контент для продвижения промышленных роботов-уборщиков.
Ниша: роботы для ТЦ, БЦ, складов, производств, уличных территорий, парковок, логистических объектов.

Тема поста:
{topic}

Сделай ответ строго в JSON-формате без пояснений и без markdown.
Нужны поля:
title
description
message
body_html
image_prompt

Требования:
- title: сильный понятный заголовок на русском
- description: 1 короткий абзац, 140-200 символов
- message: текст для поста VK на 600-1200 символов, без воды, с пользой, с нормальным раскрытием темы
- body_html: HTML для страницы поста, минимум 3 абзаца и 1 список
- image_prompt: подробный промпт на русском для генерации реалистичной картинки по теме
- не используй эмодзи
- не пиши, что текст создан ИИ
- стиль: экспертный, продающий, понятный для владельцев и управляющих объектами
- без повторов формулировок
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.9,
        messages=[
            {
                "role": "system",
                "content": "Ты сильный русскоязычный маркетинговый редактор для B2B-контента."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)
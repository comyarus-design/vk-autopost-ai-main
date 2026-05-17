from app.page_generator import render_post_page

result = render_post_page(
    title="Тест превью VK",
    description="Тестовая страница для VK Open Graph превью.",
    body_html="<p>Это тестовая HTML-страница, которую VK должен использовать для предпросмотра.</p>",
    image_rel_path="content/images/og-preview.jpg",
    slug="test-prevyu-vk"
)

print(result)

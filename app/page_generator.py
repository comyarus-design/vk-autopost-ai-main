import re
from pathlib import Path
from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader

GITHUB_USERNAME = "comyarus-design"
REPO_NAME = "vk-autopost-ai"
PAGES_BASE_URL = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("ё", "e")

    ru_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l",
        "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s",
        "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
        "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e",
        "ю": "yu", "я": "ya"
    }

    text = "".join(ru_map.get(ch, ch) for ch in text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "post"


def render_post_page(
    title: str,
    description: str,
    body_html: str,
    image_rel_path: str,
    slug: str | None = None,
) -> dict:
    template_dir = Path("templates")
    output_dir = Path("content/pages")
    output_dir.mkdir(parents=True, exist_ok=True)

    final_slug = slugify(slug or title)
    output_file = output_dir / f"{final_slug}.html"

    clean_image_rel_path = image_rel_path.replace("\\", "/").lstrip("./")
    image_name = Path(clean_image_rel_path).name
    safe_image_name = quote(image_name)
    image_url = f"{PAGES_BASE_URL}/content/images/{safe_image_name}"

    page_rel_path = f"content/pages/{final_slug}.html"
    page_url = f"{PAGES_BASE_URL}/{page_rel_path}"

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("post_page.html")

    html = template.render(
        title=title,
        description=description,
        body_html=body_html,
        image_url=image_url,
        page_url=page_url,
    )

    output_file.write_text(html, encoding="utf-8")

    return {
        "slug": final_slug,
        "page_path": page_rel_path,
        "page_url": page_url,
        "image_url": image_url,
    }
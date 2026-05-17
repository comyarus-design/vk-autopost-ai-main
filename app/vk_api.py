import os
import requests
from dotenv import load_dotenv
from config.settings import VK_GROUP_TOKEN, VK_API_VERSION, VK_GROUP_ID

load_dotenv(override=True)


class VKAPIError(Exception):
    pass


def _get_user_token() -> str | None:
    token = os.getenv("VK_USER_TOKEN", "").strip()
    print(f"DEBUG_HAS_USER_TOKEN={bool(token)}")
    return token or None


def vk_method(method: str, params: dict | None = None, token: str | None = None) -> dict:
    access_token = token or VK_GROUP_TOKEN
    if not access_token:
        raise VKAPIError("VK access token is empty")

    url = f"https://api.vk.com/method/{method}"
    payload = params.copy() if params else {}
    payload["access_token"] = access_token
    payload["v"] = VK_API_VERSION

    response = requests.post(url, data=payload, timeout=30)
    data = response.json()

    if "error" in data:
        error = data["error"]
        code = error.get("error_code")
        msg = error.get("error_msg")
        raise VKAPIError(f"VK API error {code}: {msg}")

    return data["response"]


def upload_wall_photo(image_path: str) -> str:
    user_token = _get_user_token()
    if not user_token:
        raise VKAPIError("VK_USER_TOKEN is empty")

    group_id = str(VK_GROUP_ID).strip().replace("-", "")
    print(f"DEBUG_UPLOAD_IMAGE_PATH={image_path}")
    print(f"DEBUG_GROUP_ID={group_id}")

    upload_server = vk_method(
        "photos.getWallUploadServer",
        {"group_id": group_id},
        token=user_token,
    )
    upload_url = upload_server["upload_url"]

    with open(image_path, "rb") as f:
        upload_response = requests.post(
            upload_url,
            files={"photo": f},
            timeout=60,
        )

    upload_data = upload_response.json()

    saved = vk_method(
        "photos.saveWallPhoto",
        {
            "group_id": group_id,
            "photo": upload_data["photo"],
            "server": upload_data["server"],
            "hash": upload_data["hash"],
        },
        token=user_token,
    )

    photo = saved[0]
    owner_id = photo["owner_id"]
    media_id = photo["id"]
    return f"photo{owner_id}_{media_id}"


def post_to_wall(message: str, link_url: str | None = None, image_path: str | None = None) -> dict:
    group_id = str(VK_GROUP_ID).strip().replace("-", "")
    owner_id = f"-{group_id}"

    attachments = []

    if image_path:
        if not os.path.exists(image_path):
            raise VKAPIError(f"Image file not found: {image_path}")
        photo_attachment = upload_wall_photo(image_path)
        attachments.append(photo_attachment)

    final_message = message
    if link_url:
        final_message = f"{message}\n\n{link_url}"

    params = {
        "owner_id": owner_id,
        "from_group": 1,
        "message": final_message,
    }

    if attachments:
        params["attachments"] = ",".join(attachments)

    print(f"WALL_POST_PARAMS={params}")
    print(f"DEBUG_IMAGE_PATH={image_path}")
    print(f"DEBUG_ATTACHMENTS={attachments}")

    return vk_method("wall.post", params)

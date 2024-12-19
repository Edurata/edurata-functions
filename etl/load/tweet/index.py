import requests
import os

bearer_token = os.environ.get("BEARER_TOKEN")
if not bearer_token:
    raise Exception("Please set the environment variable: BEARER_TOKEN")


def create_headers():
    return {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }


def upload_media(media_path):
    url = "https://upload.twitter.com/1.1/media/upload.json"
    headers = create_headers()
    files = {"media": open(media_path, "rb")}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise Exception(f"Media upload failed: {response.text}")
    return response.json()["media_id_string"]


def create_tweet(text, media_id=None):
    url = "https://api.twitter.com/2/tweets"
    headers = create_headers()
    payload = {"text": text}

    if media_id:
        payload["media"] = {"media_ids": [media_id]}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Tweet creation failed: {response.text}")
    return response.json()


def tweet(text: str, media: str = None):
    print("Tweeting:", text, media)

    if not text or len(text) > 280:
        print("Warning: Text exceeds the maximum allowed length (280 characters). Skipping tweet.")
        return

    media_id = None
    if media:
        media_id = upload_media(media)

    return create_tweet(text, media_id)


def handler(inputs):
    tweet(inputs["message"], inputs.get("mediaPath"))
    return {
        "success": True
    }


if __name__ == "__main__":
    print(handler({
        "message": "Hello World!",
        "mediaPath": "./__tests__/test.png"
    }))

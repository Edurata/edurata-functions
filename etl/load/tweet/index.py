import tweepy
import os

consumer_key = os.environ.get("API_KEY")
consumer_secret = os.environ.get("API_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")
if not consumer_key or not consumer_secret or not access_token or not access_token_secret:
    raise Exception("Please set the environment variables: API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET")


def get_api_v1():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    client = tweepy.API(auth)
    return client

def get_api_v2():
    client = api = tweepy.Client(bearer_token=bearer_token,
        access_token=access_token,
        access_token_secret=access_token_secret,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret)

    return client

def tweet(text: str, media: str = None):
    print("Tweeting:", text, media)
    
    # Check the length of the text
    if not text or (text and len(text) > 280):
        print("Warning: Text exceeds the maximum allowed length (280 characters). Skipping tweet.")
        return

    apiV1 = get_api_v1()
    apiV2 = get_api_v2()
    media_ids = None
    
    if media:
        media_ids = [apiV1.media_upload(media).media_id_string]

    # return apiV1.update_status(text, media_ids=media_ids)
    return apiV2.create_tweet(text=text, media_ids=media_ids)

def handler(inputs):
    for index, element in enumerate(inputs["messages"]):
        tweet(inputs["messages"][index], inputs["mediaPaths"][index] if "mediaPaths" in inputs and inputs["mediaPaths"][index] else None)
    return {
        "success": True
    }

if __name__ == "__main__":
    handler({
        "messages": ["Hello World"],
        "mediaPaths": ["./__tests__/test.png"]
    })
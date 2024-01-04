import tweepy
import os

def get_api():
    consumer_key = os.environ.get("API_KEY")
    consumer_secret = os.environ.get("API_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    if not consumer_key or not consumer_secret or not access_token or not access_token_secret:
        raise Exception("Please set the environment variables: API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    client = tweepy.API(auth)
    return client

def tweet(text: str, media: str = None):
    print("Tweeting: ", text, media)
    api = get_api()
    if media:
        media_ids = [api.media_upload(media).media_id_string]
        return api.update_status(text, media_ids=media_ids)
    return api.update_status(text)

def handler(inputs):
    for index, element in enumerate(inputs["messages"]):
        tweet(inputs["messages"][index], inputs["mediaPaths"][index])
    return {
        success: True
    }

if __name__ == "__main__":
    handler({
        "messages": ["Hello World"],
        "mediaPaths": ["./test.png"]
    })
import tweepy

def tweet(text: str, media: str = None):
    api = api()
    if media:
        media_ids = [api.media_upload(media).media_id_string]
        return api.update_status(text, media_ids=media_ids)
    return api.update_status(text)

def api():
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    if not consumer_key or not consumer_secret or not access_token or not access_token_secret:
        raise Exception("Please set the environment variables: CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    client = tweepy.API(auth)
    return client

def handler(inputs):
    tweet(inputs.message, inputs.media)
    return inputs.message

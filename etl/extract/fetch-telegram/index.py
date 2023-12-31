import asyncio
from telethon.sync import TelegramClient
import os
import logging
from telethon.tl.types import MessageMediaPhoto
from datetime import datetime, timedelta, timezone
from telethon.sessions import StringSession
import json
# Replace with your own credentials
api_id = os.environ.get('TELEGRAM_API_ID')
api_hash = os.environ.get('TELEGRAM_API_HASH')
session = os.environ.get('TELEGRAM_API_SESSION') 
async def get_posts(client, channel_id, since_days, image_dir, limit=100):
    # Directory to save images
    os.makedirs(image_dir, exist_ok=True)
    await client.start()
    channel = await client.get_entity(channel_id)
    return_messages = []
    # Define the time limit (3 days ago)
    time_limit = datetime.now(timezone.utc) - timedelta(days=int(since_days))

    messages = await client.get_messages(channel, limit=limit)

    for message in messages:
        if not message.media:
            continue
        # Check if the message date is within the last 3 days
        if message.date > time_limit:
            new_message = {}
            new_message["id"] = message.id
            new_message["text"] = message.text
        
            print("processed message:", message.id, message.text)
            if message.media and isinstance(message.media, MessageMediaPhoto):
                # Download photo
                path = await message.download_media(file=image_dir)
                new_message["mediaPath"] = path
                print(f"Downloaded to {path}")
            return_messages.append(new_message)
        else:
            # Break the loop if message is older than 3 days
            break

    return return_messages

def handler(inputs):
    print("Starting the function")
    # Initialize the client
    with TelegramClient(StringSession(session), api_id, api_hash) as client:
        if (session == None):
            # If no session is provided, generate a new one
            print("Generating new session. Save this to your environment variables")
            print(client.session.save())

        channel_id = inputs["channelId"]
        since_days = inputs["sinceDays"]
        image_dir = inputs["imageDir"]
        loop = asyncio.get_event_loop()
        print(f"Fetching posts from {channel_id} since {since_days} days ago")
        posts = loop.run_until_complete(get_posts(client, channel_id, since_days, image_dir))
        print("Finished fetching posts")
        print("Posts: ", posts)
        # map to only the attributes we need
        return {
            "posts": posts
        }

if __name__ == '__main__':
    # For local testing
    inputs = {
        "channelId": "knVknVknV",
        "sinceDays": 3,
        "imageDir": "downloaded_images"
    }

    returned = handler(inputs)
    print(json.loads(json.dumps(returned)))
import asyncio
from telethon import TelegramClient
import os
import logging
from telethon.tl.types import MessageMediaPhoto
from datetime import datetime, timedelta, timezone

# Replace with your own credentials
api_id = os.environ.get('TELEGRAM_API_ID')
api_hash = os.environ.get('TELEGRAM_API_HASH')

async def get_posts(client, channel_id, since_days, image_dir, limit=100):
    # Directory to save images
    os.makedirs(image_directory, exist_ok=True)
    await client.start()
    channel = await client.get_entity(channel_id)

    # Define the time limit (3 days ago)
    time_limit = datetime.now(timezone.utc) - timedelta(days=pull_since_days)

    messages = await client.get_messages(channel, limit=limit)

    for message in messages:
        # Check if the message date is within the last 3 days
        if message.date > time_limit:
            print(message.id, message.text)
            if message.media and isinstance(message.media, MessageMediaPhoto):
                # Download photo
                path = await message.download_media(file=image_directory)
                message.mediaPaths = path
                print(f"Downloaded to {path}")
        else:
            # Break the loop if message is older than 3 days
            break

    return messages

def handler(inputs):
    # Initialize the client
    client = TelegramClient('main', api_id, api_hash)
    channel_id = inputs["channelId"]
    since_days = inputs["sinceDays"]
    image_dir = inputs["imageDir"]
    posts = get_posts(client, channel_id, since_days, image_dir)

    return {
        "posts": posts,
        "mediaPaths": "downloaded_images/*"
    }

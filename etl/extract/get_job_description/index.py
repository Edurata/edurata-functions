import os
import requests

def handler(inputs):
    NOTION_API_KEY = inputs.get("notion_api_key")  # Get API Key from inputs
    if not NOTION_API_KEY:
        return {"error": "NOTION_API_KEY is missing. Ensure it's set in Edurata Secrets."}

    notion_page_id = inputs.get("notion_page_id")
    if not notion_page_id:
        return {"error": "notion_page_id is required but was not provided."}

    url = f"https://api.notion.com/v1/blocks/{notion_page_id}/children"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"Failed to fetch Notion page: {response.text}"}

    data = response.json()
    blocks = data.get("results", [])
    content = ""

    # Extract text from blocks
    for block in blocks:
        block_type = block.get("type")
        block_data = block.get(block_type, {})

        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            text_elements = block_data.get("rich_text", [])
            text = "".join([part.get("plain_text", "") for part in text_elements])
            content += text + " "

    return {"job_description": content.strip() if content else "No text found"}
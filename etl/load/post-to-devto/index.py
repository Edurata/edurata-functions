import requests
import os

def handler(inputs):
    url = "https://dev.to/api/articles"
    api_key = inputs.get("apiKey") or os.environ.get("API_KEY")
    if not api_key:
        return {"articleId": "", "message": "Missing API key"}
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "article": {
            "title": inputs['title'],
            "body_markdown": inputs['bodyMarkdown'],
            "tags": inputs.get('tags', []),
            "series": inputs.get('series', None),
            "published": inputs.get('published', False)
        }
    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    if response.status_code in [200, 201]:
        return {"articleId": str(response_data['id']), "message": "Article created successfully."}
    else:
        return {"articleId": "", "message": response_data.get('error', 'Unknown error')}

# Sample call (commented out)
# print(handler({
#     "apiKey": "your_api_key_here",
#     "title": "My First Dev.to Article",
#     "bodyMarkdown": "# Heading\nThis is some content.",
#     "tags": ["Python", "API"],
#     "published": False
# }))

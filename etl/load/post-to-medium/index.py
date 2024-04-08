import requests
import os

def handler(inputs):
    url = "https://api.medium.com/v1/users/me/posts"
    headers = {
        "Authorization": f"Bearer {os.environ['ACCESS_TOKEN']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "title": inputs['title'],
        "contentFormat": inputs['contentFormat'],
        "content": inputs['content'],
        "tags": inputs.get('tags', []),
        "publishStatus": inputs['publishStatus']
    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    if response.status_code == 201:
        return {"postId": response_data['data']['id'], "message": "Post created successfully."}
    else:
        return {"postId": "", "message": response_data.get('errors', 'Unknown error')}

# Sample call (commented out)
# print(handler({
#     "accessToken": "your_access_token_here",
#     "title": "My First Post",
#     "content": "<h1>This is a heading</h1><p>This is a paragraph.</p>",
#     "contentFormat": "html",
#     "tags": ["Python", "API"],
#     "publishStatus": "draft"
# }))

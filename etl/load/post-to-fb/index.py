import requests

def handler(inputs):
    url = f"https://graph.facebook.com/{inputs['pageId']}/feed"
    params = {
        "access_token": inputs['accessToken'],
        "message": inputs['message']
    }
    response = requests.post(url, params=params)
    response_data = response.json()
    if response.status_code == 200:
        return {
            "postId": response_data['id'],
            "message": "Post created successfully on Facebook."
        }
    else:
        return {
            "postId": "",
            "message": response_data.get('error', {}).get('message', 'Failed to create post on Facebook.')
        }

# Sample call (commented out)
# print(handler({
#     "accessToken": "your_access_token_here",
#     "pageId": "your_page_id_here",
#     "message": "Hello, Facebook!"
# }))

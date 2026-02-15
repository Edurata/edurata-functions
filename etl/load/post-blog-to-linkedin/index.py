import requests

def handler(inputs):
    url = "https://api.linkedin.com/v2/shares"
    headers = {
        "Authorization": f"Bearer {inputs['accessToken']}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    data = {
        "owner": inputs['author'],
        "subject": inputs['title'],
        "text": {
            "text": inputs['content']
        },
        "distribution": {
            "linkedInDistributionTarget": {}
        },
        "content": {
            "contentEntities": [
                {
                    "entityLocation": "",
                    "thumbnails": [
                        {
                            "resolvedUrl": ""
                        }
                    ]
                }
            ],
            "title": inputs['title'],
            "shareMediaCategory": inputs['shareMediaCategory']
        },
        "commentary": {
            "text": inputs['shareCommentary']
        }
    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    if response.status_code == 201:
        return {
            "shareId": response_data['activity'],
            "message": "Article posted successfully to LinkedIn."
        }
    else:
        return {
            "shareId": "",
            "message": response_data.get('message', 'Failed to post article to LinkedIn.'),
            "status": response.status_code
        }

# Sample call (commented out)
# print(handler({
#     "accessToken": "your_access_token_here",
#     "author": "urn:li:person:ABC123XYZ",
#     "title": "My LinkedIn Article Title",
#     "content": "This is the body of my LinkedIn article.",
#     "shareCommentary": "Check out my latest article!",
#     "shareMediaCategory": "ARTICLE"
# }))

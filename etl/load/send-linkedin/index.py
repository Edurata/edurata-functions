import os
import requests

def handler(inputs):
    linkedin_api_secret = os.environ.get("LINKEDIN_API_SECRET")
    text = inputs.get("text")
    media_paths = inputs.get("mediaPaths", [])
    
    access_token = get_access_token(linkedin_api_secret)  # Placeholder for actual implementation
    media_ids = upload_media(media_paths, access_token) if media_paths else []
    
    post_url = "https://api.linkedin.com/v2/posts"
    post_data = create_post_data(text, media_ids)
    
    response = requests.post(post_url, headers={"Authorization": f"Bearer {access_token}"}, json=post_data)
    return {"status": response.status_code, "response": response.json()}

def get_access_token(linkedin_api_secret):
    # Placeholder for access token retrieval logic
    return "your_access_token"

def upload_media(media_paths, access_token):
    media_ids = []
    upload_url = "https://api.linkedin.com/v2/mediaUpload"  # This URL is hypothetical and will likely differ
    
    for media_path in media_paths:
        files = {'file': open(media_path, 'rb')}
        # LinkedIn's actual media upload API might require additional headers or data fields
        response = requests.post(upload_url, headers={"Authorization": f"Bearer {access_token}"}, files=files)
        if response.status_code == 200:
            media_id = response.json().get('value').get('media')
            media_ids.append(media_id)
        else:
            print(f"Error uploading media: {media_path}")
    
    return media_ids

def create_post_data(text, media_ids):
    post_data = {
        "author": "urn:li:person:yourLinkedInPersonId",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
        }
    }
    
    if media_ids:
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"  # Or another category based on the media type
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{"status": "READY", "description": {"text": "Media description"}, "media": media_id} for media_id in media_ids]
    
    return post_data

# Sample function call (commented out)
# print(handler({"text": "Hello LinkedIn!", "mediaPaths": ["path/to/media1.jpg", "path/to/media2.mp4"]}))

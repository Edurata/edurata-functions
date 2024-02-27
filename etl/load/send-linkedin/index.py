import os
import requests
import json

def handler(inputs):
    text = inputs.get("text")
    media_type = inputs.get("mediaType", "image")  # New input for media type ("image", "video", "document", "multiImage", "carousel")
    media_paths = inputs.get("mediaPaths", [])
    sponsored = inputs.get("sponsored", False)  # New input to indicate if the post is sponsored
    author = inputs.get("author", None)  # Replace 'YOUR_ORG_ID' with your actual LinkedIn organization ID

    access_token = get_access_token()
    print(access_token)
    media_ids = upload_media(media_paths, media_type, access_token, author) if media_paths else []
    
    post_url = "https://api.linkedin.com/rest/posts"
    post_data = create_post_data(text, media_ids, media_type, author, sponsored)
    
    response = requests.post(post_url, headers={"LinkedIn-Version": "202304", "Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}, json=post_data)
    return {"status": response.status_code, "response": response.text}

def get_access_token():
    token = os.environ.get("LINKEDIN_API_TOKEN")
    if token:
        return token
    with open('.token', 'r') as file:
        return file.read()

def upload_media(media_paths, media_type, access_token, author):
    media_ids = []
    for media_path in media_paths:
        if media_type == "image":
            media_id = upload_image(media_path, access_token, author)
        elif media_type == "video":
            # Placeholder: implement video upload logic here
            media_id = None  # Replace None with the actual media ID obtained after uploading the video
        elif media_type == "document":
            # Placeholder: implement document upload logic here
            media_id = None  # Replace None with the actual media ID obtained after uploading the document
        else:
            print(f"Unsupported media type: {media_type}")
            continue

        if media_id:
            media_ids.append(media_id)
        else:
            print(f"Failed to upload media: {media_path}")

    return media_ids

def upload_image(media_path, access_token, author):
    initialize_upload_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
    headers = {"Authorization": f"Bearer {access_token}", "LinkedIn-Version": "202304"}
    # Initialize the upload to get the upload URL
    init_response = requests.post(
        initialize_upload_url,
        headers=headers,
        json={"initializeUploadRequest": {"owner": author}}
    )
    
    if init_response.status_code == 200:
        upload_details = init_response.json()['value']
        upload_url = upload_details['uploadUrl']
        image_urn = upload_details['image']
        
        # Upload the image
        with open(media_path, 'rb') as image_file:
            upload_response = requests.put(upload_url, headers=headers, data=image_file.read())
        
        if upload_response.status_code in [200, 201]:
            return image_urn
        else:
            print(f"Error uploading image: {media_path}, Status Code: {upload_response.text}")
    else:
        print(f"Error initializing upload for image: {media_path}, Status Code: {init_response.text}")
    
    return None

def create_post_data(text, media_ids, media_type, author, sponsored):
    post_data = {
        "author": author,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    
    if media_type in ["image", "video", "document", "multiImage", "carousel"]:
        media_content = []

        if len(media_ids) > 1:
            for media_id in media_ids:
                media_item = {"altText": "Media Title", "id": media_id}  # Adjust this based on actual requirements
                media_content.append(media_item)
        elif len(media_ids) == 1:
            media_content = {"title": "Media Title", "id": media_ids[0]}
        if media_type == "multiImage" and not sponsored:
            # Placeholder for MultiImage API specific structure
            pass  # Adjust accordingly
        elif media_type == "carousel" and sponsored:
            # Placeholder for Carousel API specific structure
            pass  # Adjust accordingly
        else:
            post_data["content"] = {"media": media_content} if media_content else {}
    
    return post_data

# Note: Replace 'YOUR_ORG_ID' with your actual LinkedIn organization ID.
# Sample function call (commented out)
print(handler({"text": "Hello LinkedIn!", "mediaPaths": ["test/test.png"], "mediaType": "image", "sponsored": False, "author": "urn:li:organization:30718435"}))

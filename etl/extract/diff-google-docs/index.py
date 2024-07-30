import requests
from difflib import unified_diff
import os

def get_document_content(document_id, revision_id, api_token):
    url = f'https://docs.googleapis.com/v1/documents/{document_id}?revisionId={revision_id}'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        print(response.json())
        return None

def handler(inputs):
    api_token = os.getenv('API_TOKEN')
    document_id = inputs['document_id']

    # Get list of revisions
    url = f'https://docs.googleapis.com/v1/documents/{document_id}/revisions'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        revisions = response.json().get('revisions', [])
        if len(revisions) >= 2:
            # Get content of the latest two revisions
            latest_revision_id = revisions[-1]['revisionId']
            previous_revision_id = revisions[-2]['revisionId']
            
            latest_content = get_document_content(document_id, latest_revision_id, api_token)
            previous_content = get_document_content(document_id, previous_revision_id, api_token)
            
            if latest_content and previous_content:
                # Extract the text content from the document structure
                latest_text = latest_content.get('body', {}).get('content', [])
                previous_text = previous_content.get('body', {}).get('content', [])
                
                # Convert the document content to plain text
                def extract_text(content):
                    return ''.join([element.get('textRun', {}).get('content', '') for element in content])
                
                latest_text = extract_text(latest_text)
                previous_text = extract_text(previous_text)
                
                # Use difflib to find the differences
                diff = unified_diff(previous_text.splitlines(), latest_text.splitlines(), lineterm='')
                differences = '\n'.join(line for line in diff)
                return {'differences': differences}
        else:
            return {'error': 'Not enough revisions to compare.'}
    else:
        return {'error': f'Error: {response.status_code}', 'details': response.json()}

# Sample function call
# print(handler({'document_id': 'YOUR_DOCUMENT_ID'}))

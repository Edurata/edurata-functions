import json
import os
import boto3
from google_images_search import GoogleImagesSearch

# Replace these with your Google Custom Search API key and CX
your_dev_api_key = os.environ.get('GOOGLE_API_KEY')
your_project_cx = os.environ.get('GOOGLE_PROJECT_CX')


def handler(inputs):

    searches = inputs.searches

    # Initialize GoogleImagesSearch object
    gis = GoogleImagesSearch(your_dev_api_key, your_project_cx)

    # Initialize boto3 S3 client
    s3_client = boto3.client('s3')

    # Iterate through each search in the JSON file
    for per_index, search in enumerate(searches):
        if per_index < 0:
            continue
        print(f"Downloading image for {search['search']}... at index {per_index}")
        search_query = f"{search['search']}"  # Construct search query
        _search_params = {
            'q': search_query,
            'num': inputs.limit if inputs.limit else 1,
            'fileType': 'jpg',
        }

        # Search and download
        gis.search(search_params=_search_params, path_to_dir='/tmp/', custom_image_name=search['id'])
        results = gis.results()

        return {
            images: map(lambda result: result.path, results)
        }

if __name__ == "__main__":
    handler({
        searches: [
            {
                "id": "1",
                "search": "wef"
            },
            {
                "search": "world economic forum"
            }
        ]
    })
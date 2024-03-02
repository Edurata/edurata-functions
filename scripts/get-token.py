import os
import json
import requests
import webbrowser
import sys

# Function to extract parameter value from URL
def get_parameter_value(url, parameter_name):
    return url.split(parameter_name + '=')[1].split('&')[0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <base_path>")
        sys.exit(1)
    
    base_path = sys.argv[1]

    # Load public and secret JSON files
    with open(os.path.join(base_path, 'oauth-public.json')) as public_file:
        public_config = json.load(public_file)

    with open(os.path.join(base_path, 'oauth-private.json')) as secret_file:
        secret_config = json.load(secret_file)

    # OAuth URLs and response type
    authorization_url = public_config['authorization_url']
    response_type = public_config.get('response_type', 'code')
    access_token_url = public_config.get('access_token_url')  # Get access token URL if defined

    # Prompting the user to enter values for placeholders in the authorization URL
    client_id = secret_config['client_id']
    scope = secret_config['scope']
    state = secret_config['state']
    redirect_uri = secret_config['redirect_uri']

    # Constructing the authorization URL
    authorization_url = f"{authorization_url}?response_type={response_type}&client_id={client_id}&scope={scope}&state={state}&redirect_uri={redirect_uri}"

    # Opening the authorization URL in a browser
    webbrowser.open(authorization_url)

    # Prompting the user to enter the authorization code
    authorization_code = input("Enter the authorization code from the redirected URL: ")

    # Prompting the user to enter the client secret
    client_secret = secret_config['client_secret']

    # Constructing the access token URL and getting access token if access token URL is defined
    if access_token_url:
        access_token_url = f"{access_token_url}"
        access_token_response = requests.post(access_token_url, data={
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }).json()

        # Extracting access token from the response
        access_token = access_token_response['access_token']
        print("Access Token:", access_token)

        # Writing the access token to the file
        token_path = os.path.join(base_path, '.token')
        with open(token_path, 'w') as token_file:
            token_file.write(access_token)
        print(f"Access token saved to {token_path}")
    else:
        print("Access token URL is not defined. Skipping access token retrieval.")

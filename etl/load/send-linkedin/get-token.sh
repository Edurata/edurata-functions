#!/bin/bash

# Function to extract parameter value from URL
get_parameter_value() {
    local url="$1"
    local parameter_name="$2"
    echo "$url" | grep -o "${parameter_name}=[^&]*" | cut -d'=' -f2
}

# OAuth URLs
authorization_url="https://www.linkedin.com/oauth/v2/authorization"
access_token_url="https://www.linkedin.com/oauth/v2/accessToken"

# Prompting the user to enter values for placeholders in the authorization URL
read -p "Enter the client ID: " client_id
read -p "Enter the scope: " scope
read -p "Enter the state: " state
read -p "Enter the redirect URI: " redirect_uri

# Constructing the authorization URL
authorization_url="${authorization_url}?response_type=code&client_id=${client_id}&scope=${scope}&state=${state}&redirect_uri=${redirect_uri}"

# Opening the authorization URL in a browser
if command -v xdg-open &>/dev/null; then
    xdg-open "$authorization_url" 2>/dev/null &
elif command -v open &>/dev/null; then
    open "$authorization_url" >/dev/null 2>&1 &
else
    echo "Cannot open the authorization URL. Please visit the following URL in your browser manually:"
    echo "$authorization_url"
fi

# Prompting the user to enter the authorization code
read -p "Enter the authorization code from the redirected URL: " authorization_code

# Prompting the user to enter the client secret
read -p "Enter the client secret: " client_secret

# Constructing the access token URL
access_token_url="${access_token_url}"

# Sending a POST request to get the access token
access_token_response=$(curl -s -d "grant_type=authorization_code&code=${authorization_code}&redirect_uri=${redirect_uri}&client_id=${client_id}&client_secret=${client_secret}" -H "Content-Type: application/x-www-form-urlencoded" -X POST "$access_token_url")

# Extracting access token from the response
access_token="$(echo "$access_token_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)"
export LINKEDIN_API_SECRET=$access_token
echo $access_token > .token
echo "Access Token: $access_token"

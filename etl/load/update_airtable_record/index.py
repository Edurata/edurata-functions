import requests

def handler(inputs):
    # Fetch inputs safely
    airtable_base_id = inputs.get("airtable_base_id")
    airtable_table_id = inputs.get("airtable_table_id")
    record_id = inputs.get("record_id")
    generated_content = inputs.get("generated_content")
    api_key = inputs.get("airtable_api_key")

    # Validate inputs
    if not api_key:
        return {"error": "AIRTABLE_API_KEY is missing. Ensure it's set in Edurata Secrets."}
    if not airtable_base_id:
        return {"error": "airtable_base_id is missing."}
    if not airtable_table_id:
        return {"error": "airtable_table_id is missing."}
    if not record_id:
        return {"error": "record_id is missing."}
    if not generated_content:
        return {"error": "generated_content is missing."}

    # Construct Airtable API request
    url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": {
            "Generated Content": generated_content,
            "Status": "processed"
        }
    }

    # Send PATCH request
    response = requests.patch(url, headers=headers, json=data)

    # Error handling
    if response.status_code == 401:
        return {"error": "Authentication failed. Check if the AIRTABLE_API_KEY is correct and has write permissions."}
    elif response.status_code == 403:
        return {"error": "Access denied. Ensure the API key has proper permissions to update this table."}
    elif response.status_code != 200:
        return {"error": f"Airtable API error {response.status_code}: {response.text}"}

    return {"status": "success", "updated_record": response.json()}

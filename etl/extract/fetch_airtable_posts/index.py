import requests

def handler(inputs):
    # Fetch API Key from inputs to ensure it's passed correctly
    api_key = inputs.get("airtable_api_key")
    if not api_key:
        return {"error": "AIRTABLE_API_KEY is missing. Ensure it is set in Edurata Secrets."}

    # Fetch Airtable Base & Table ID
    airtable_base_id = inputs.get("airtable_base_id")
    airtable_table_id = inputs.get("airtable_table_id")

    if not airtable_base_id:
        return {"error": "airtable_base_id is missing."}
    
    if not airtable_table_id:
        return {"error": "airtable_table_id is missing."}

    # Airtable API request
    url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",  # Ensure correct header format
        "Content-Type": "application/json"
    }
    params = {
        "filterByFormula": "AND({Status}='unprocessed')",
        "maxRecords": 10
    }

    # Send GET request
    response = requests.get(url, headers=headers, params=params)

    # Error Handling
    if response.status_code == 401:
        return {"error": "Authentication failed. Check if the AIRTABLE_API_KEY is correct and has read access."}
    elif response.status_code == 403:
        return {"error": "Access denied. Ensure the API key has proper permissions to read this table."}
    elif response.status_code != 200:
        return {"error": f"Airtable API error {response.status_code}: {response.text}"}

    return {"records": response.json().get("records", [])}

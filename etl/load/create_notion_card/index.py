import requests
import json

def handler(inputs):
    NOTION_API_KEY = inputs.get("notion_api_key")
    if not NOTION_API_KEY:
        return {"error": "NOTION_API_KEY is missing."}

    database_id = inputs.get("notion_database_id")
    if not database_id:
        return {"error": "notion_database_id is missing."}

    company_name = inputs.get("company_name", "Unknown")
    job_name = inputs.get("job_name", "Unknown")
    short_description = inputs.get("short_job_description", "No description provided.")
    language = inputs.get("language", "Unknown")
    working_model = inputs.get("working_model", "Unknown")
    location = inputs.get("location", "Unknown")
    role = inputs.get("role", "Unknown")

    # Convert salary expectation to a number or null
    try:
        salary_expectation = float(inputs.get("salary_expectation", 0))
    except ValueError:
        salary_expectation = None  # If not numeric, store as None
    
    iso_time = inputs.get("iso_time", None)

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Company Name": {"title": [{"text": {"content": company_name}}]},
            "Status": {"status": {"name": "Not applied"}},
            "Date": {"date": {"start": iso_time} if iso_time else None},
            "Job Name": {"rich_text": [{"text": {"content": job_name}}]},
            "Job Description": {"rich_text": [{"text": {"content": short_description}}]},
            "Language": {"rich_text": [{"text": {"content": language}}]},
            "Working Model": {"rich_text": [{"text": {"content": working_model}}]},
            "Location": {"rich_text": [{"text": {"content": location}}]},
            "Role": {"rich_text": [{"text": {"content": role}}]},
            "Salary Expectation": {"number": salary_expectation}
        }
    }

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    print("Payload Sent to Notion API:", json.dumps(data, indent=4))

    response = requests.post("https://api.notion.com/v1/pages", json=data, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"Failed to create Notion card: {response.text}"}
    
    notion_card = response.json()
    print(f"Successfully created Notion Card: {notion_card}")

    return {"notion_card": notion_card}  # This ensures the workflow has an output

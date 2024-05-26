import requests
import os

def create_company(api_key, company):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    data = {
        "properties": company
    }
    print("Sending data to HubSpot: ", data)
    response = requests.post(url, json=data, headers=headers)
    print("Response from HubSpot: ", response.text)
    if response.status_code == 201:
        return {"company_id": response.json()["id"], "status": "success"}
    else:
        return {"company_id": None, "status": "failure", "error": response.text}

def handler(inputs):
    api_key = os.getenv("HUBSPOT_API_KEY")
    if (api_key == None):
        return {"error": "API key not found."}
    print(api_key)
    companies = inputs.get("companies", [])
    results = []
    for company in companies:
        result = create_company(api_key, company)
        results.append(result)
    return {"result": results}

# Sample function call
inputs = {
    "companies": [
        {
            "name": "Example Company",
            "domain": "example.com",
        }
    ]
}
print(handler(inputs))

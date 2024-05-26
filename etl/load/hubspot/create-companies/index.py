import requests
import os

def create_company(api_key, company):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    data = {
        "properties": {
            "name": company["name"],
            "domain": company["domain"]
        }
    }

    for key, value in company.get("additional_properties", {}).items():
        data["properties"][key] = value

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return {"company_id": response.json()["id"], "status": "success"}
    else:
        return {"company_id": None, "status": "failure", "error": response.text}

def handler(inputs):
    api_key = os.getenv("HUBSPOT_API_KEY")
    companies = inputs.get("companies", [])
    results = []
    for company in companies:
        result = create_company(api_key, company)
        results.append(result)
    return {"result": results}

# Sample function call
# inputs = {
#     "companies": [
#         {
#             "name": "Example Company",
#             "domain": "example.com",
#             "additional_properties": {"phone": "1234567890"}
#         }
#     ]
# }
# print(handler(inputs))

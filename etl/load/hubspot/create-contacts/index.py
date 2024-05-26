import requests
import os

def create_contact(api_key, contact):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    data = {
        "properties": {
            "email": contact["email"],
            "firstname": contact["firstname"],
            "lastname": contact["lastname"],
        },
        "associations": []
    }

    if "company_hubspot_id" in contact:
        data["associations"].append({
            "to": {
                "id": contact["company_hubspot_id"]
            },
            "types": [
                {
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": 279
                }
            ]
        })
    print("Sending data to HubSpot: ", data)

    response = requests.post(url, json=data, headers=headers)
    print("Response from HubSpot: ", response.text)
    if response.status_code == 200:
        return {"contact_id": response.json()["vid"], "status": "success"}
    else:
        return {"contact_id": None, "status": "failure", "error": response.text}

def handler(inputs):
    api_key = os.getenv("HUBSPOT_API_KEY")
    contacts = inputs.get("contacts", [])
    results = []
    for contact in contacts:
        result = create_contact(api_key, contact)
        results.append(result)
    return {"result": results}

# Sample function call
# inputs = {
#     "contacts": [
#         {
#             "email": "example1@example.com",
#             "first_name": "John",
#             "last_name": "Doe",
#             "additional_properties": {"phone": "1234567890"}
#         },
#         {
#             "email": "example2@example.com",
#             "first_name": "Jane",
#             "last_name": "Smith",
#             "additional_properties": {"company": "Company Name"}
#         }
#     ]
# }
# print(handler(inputs))

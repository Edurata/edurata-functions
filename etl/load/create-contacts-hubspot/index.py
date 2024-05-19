import requests
import os

def create_contact(api_key, contact):
    url = "https://api.hubapi.com/contacts/v1/contact"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "properties": [
            {"property": "email", "value": contact["email"]},
            {"property": "firstname", "value": contact["first_name"]},
            {"property": "lastname", "value": contact["last_name"]}
        ]
    }
    for key, value in contact.get("additional_properties", {}).items():
        data["properties"].append({"property": key, "value": value})

    response = requests.post(url, json=data, headers=headers)
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

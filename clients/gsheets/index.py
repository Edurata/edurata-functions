import os
import json
import requests

def handler(inputs):
    spreadsheet_id = inputs.get('spreadsheet_id')
    range_name = inputs.get('range')
    oauth_token = inputs.get('oauth_token')
    data = inputs.get('data')

    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}'

    if data:
        # Write operation
        response = requests.put(
            url,
            headers=headers,
            params={'valueInputOption': 'RAW'},
            json={'values': data}
        )
    else:
        # Read operation
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {'response': response.json()}
    else:
        response.raise_for_status()

# Example function call
# inputs = {
#     'spreadsheet_id': 'your_spreadsheet_id',
#     'range': 'Sheet1!A1:B2',
#     'oauth_token': 'your_oauth_token',
#     'data': [['A', 'B'], ['C', 'D']]
# }
# print(handler(inputs))

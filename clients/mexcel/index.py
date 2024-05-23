import os
import json
import requests

def handler(inputs):
    workbook_id = inputs.get('workbook_id')
    worksheet_name = inputs.get('worksheet_name')
    range_name = inputs.get('range')
    oauth_token = inputs.get('oauth_token')
    data = inputs.get('data')

    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json'
    }

    url = f'https://graph.microsoft.com/v1.0/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address=\'{range_name}\')'

    if data:
        # Write operation
        response = requests.patch(
            url,
            headers=headers,
            json={'values': data}
        )
    else:
        # Read operation
        response = requests.get(url, headers=headers)

    if response.status_code in (200, 201):
        return {'response': response.json()}
    else:
        response.raise_for_status()

# Example function call
# inputs = {
#     'workbook_id': 'your_workbook_id',
#     'worksheet_name': 'Sheet1',
#     'range': 'A1:B2',
#     'oauth_token': 'your_oauth_token',
#     'data': [['A', 'B'], ['C', 'D']]
# }
# print(handler(inputs))

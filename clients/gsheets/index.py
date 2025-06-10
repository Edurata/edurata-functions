import os
import json
import requests
from openpyxl import Workbook, load_workbook
from pathlib import Path
import io
import tempfile
import pandas as pd

class SpreadsheetClient:
    def __init__(self, oauth_token=None):
        self.oauth_token = oauth_token
        if oauth_token:
            self.headers = {
                'Authorization': f'Bearer {oauth_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

    def _is_google_sheets(self, file_id):
        return file_id.startswith('http') or 'google' in file_id.lower()

    def _is_excel_in_drive(self, file_id):
        # Check if it's a Google Drive file ID (not a local path)
        return not os.path.exists(file_id) and not file_id.startswith('http')

    def _create_folder_in_drive(self, folder_name, parent_id=None):
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]

        response = requests.post(
            'https://www.googleapis.com/drive/v3/files',
            headers=self.headers,
            json=folder_metadata
        )
        if response.status_code == 200:
            return response.json()['id']
        else:
            response.raise_for_status()

    def _get_or_create_folder_path(self, path):
        # Split path into parts
        parts = path.strip('/').split('/')
        if len(parts) == 1:  # Just a filename, no folders
            return None

        # Remove filename from parts
        filename = parts[-1]
        folder_parts = parts[:-1]
        
        current_parent_id = None
        for folder_name in folder_parts:
            # Search for folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if current_parent_id:
                query += f" and '{current_parent_id}' in parents"
            
            response = requests.get(
                'https://www.googleapis.com/drive/v3/files',
                headers=self.headers,
                params={'q': query}
            )
            
            if response.status_code == 200:
                folders = response.json().get('files', [])
                if folders:
                    current_parent_id = folders[0]['id']
                else:
                    current_parent_id = self._create_folder_in_drive(folder_name, current_parent_id)
            else:
                response.raise_for_status()
        
        return current_parent_id

    def _create_file_in_drive(self, path, content=None):
        # Split path into parts
        parts = path.strip('/').split('/')
        filename = parts[-1]
        
        # Get or create folder structure
        parent_id = self._get_or_create_folder_path(path)
        
        # Create empty workbook if no content provided
        if content is None:
            wb = Workbook()
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            content = output.getvalue()

        # Create file metadata
        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        # Create file
        response = requests.post(
            'https://www.googleapis.com/upload/drive/v3/files',
            headers=self.headers,
            params={'uploadType': 'multipart'},
            files={
                'metadata': (None, json.dumps(file_metadata)),
                'file': content
            }
        )
        
        if response.status_code == 200:
            return response.json()['id']
        else:
            response.raise_for_status()

    def _get_drive_file(self, file_id):
        url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.content
        else:
            response.raise_for_status()

    def _update_drive_file(self, file_id, content):
        url = f'https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media'
        response = requests.patch(url, headers=self.headers, data=content)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def _get_file_id_by_path(self, path):
        # Search for file by name
        filename = path.split('/')[-1]
        query = f"name='{filename}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        
        # If path contains folders, get parent folder ID
        parent_id = self._get_or_create_folder_path(path)
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        response = requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=self.headers,
            params={'q': query}
        )
        
        if response.status_code == 200:
            files = response.json().get('files', [])
            if files:
                return files[0]['id']
            else:
                # File doesn't exist, create it
                return self._create_file_in_drive(path)
        else:
            response.raise_for_status()

    def read(self, file_id, range_name):
        if self._is_google_sheets(file_id):
            return self._read_google_sheets(file_id, range_name)
        elif self._is_excel_in_drive(file_id):
            return self._read_excel_from_drive(file_id, range_name)
        else:
            # Try to find or create file in Drive
            drive_file_id = self._get_file_id_by_path(file_id)
            return self._read_excel_from_drive(drive_file_id, range_name)

    def write(self, file_id, range_name, data):
        if self._is_google_sheets(file_id):
            return self._write_google_sheets(file_id, range_name, data)
        elif self._is_excel_in_drive(file_id):
            return self._write_excel_to_drive(file_id, range_name, data)
        else:
            # Try to find or create file in Drive
            drive_file_id = self._get_file_id_by_path(file_id)
            return self._write_excel_to_drive(drive_file_id, range_name, data)

    def _read_google_sheets(self, spreadsheet_id, range_name):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return {
                    'values': [],
                    'structured_values': [],
                    'headers': [],
                    'row_info': {
                        'start_row': 0,
                        'end_row': 0,
                        'total_rows': 0
                    }
                }

            # Extract headers from first row
            headers = values[0]
            
            # Parse range to get starting row and column
            range_parts = range_name.split('!')
            if len(range_parts) > 1:
                cell_range = range_parts[1]
                start_cell = cell_range.split(':')[0]
                start_col = ord(start_cell[0].upper()) - ord('A')
                start_row = int(''.join(filter(str.isdigit, start_cell)))
            else:
                start_col = 0
                start_row = 1

            # Create structured data with coordinates
            structured_values = []
            for row_idx, row in enumerate(values[1:], start=start_row + 1):
                row_data = {}
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row):
                        value = row[col_idx]
                        # Convert numeric strings to numbers
                        if value.isdigit():
                            value = int(value)
                        elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                            value = float(value)
                        row_data[header] = {
                            'value': value,
                            'location': {
                                'row': row_idx,
                                'column': chr(ord('A') + col_idx + start_col),
                                'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                            }
                        }
                    else:
                        row_data[header] = {
                            'value': None,
                            'location': {
                                'row': row_idx,
                                'column': chr(ord('A') + col_idx + start_col),
                                'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                            }
                        }
                structured_values.append(row_data)

            return {
                'values': values,
                'structured_values': structured_values,
                'headers': headers,
                'row_info': {
                    'start_row': start_row,
                    'end_row': start_row + len(values) - 1,
                    'total_rows': len(values) - 1  # Excluding header row
                }
            }
        except Exception as e:
            raise Exception(f"Error reading Google Sheets: {str(e)}")

    def _write_google_sheets(self, spreadsheet_id, range_name, data):
        url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}'
        response = requests.put(
            url,
            headers=self.headers,
            params={'valueInputOption': 'RAW'},
            json={'values': data}
        )
        
        if response.status_code == 200:
            return {'response': response.json()}
        else:
            response.raise_for_status()

    def _parse_range(self, range_name):
        sheet_name, cell_range = range_name.split('!')
        start_cell, end_cell = cell_range.split(':')
        return sheet_name, start_cell, end_cell

    def _read_excel_from_drive(self, file_id, range_name):
        try:
            # Download file from Google Drive
            file_id = self._get_file_id(file_id)
            request = self.drive_service.files().get_media(fileId=file_id)
            file_content = request.execute()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Read Excel file
                df = pd.read_excel(temp_file_path, sheet_name=range_name.split('!')[0])
                
                # Convert DataFrame to list of lists
                values = [df.columns.tolist()] + df.values.tolist()
                
                # Extract headers
                headers = values[0]
                
                # Parse range to get starting row and column
                range_parts = range_name.split('!')
                if len(range_parts) > 1:
                    cell_range = range_parts[1]
                    start_cell = cell_range.split(':')[0]
                    start_col = ord(start_cell[0].upper()) - ord('A')
                    start_row = int(''.join(filter(str.isdigit, start_cell)))
                else:
                    start_col = 0
                    start_row = 1

                # Create structured data with coordinates
                structured_values = []
                for row_idx, row in enumerate(values[1:], start=start_row + 1):
                    row_data = {}
                    for col_idx, header in enumerate(headers):
                        if col_idx < len(row):
                            value = row[col_idx]
                            row_data[header] = {
                                'value': value,
                                'location': {
                                    'row': row_idx,
                                    'column': chr(ord('A') + col_idx + start_col),
                                    'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                                }
                            }
                        else:
                            row_data[header] = {
                                'value': None,
                                'location': {
                                    'row': row_idx,
                                    'column': chr(ord('A') + col_idx + start_col),
                                    'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                                }
                            }
                    structured_values.append(row_data)

                return {
                    'values': values,
                    'structured_values': structured_values,
                    'headers': headers,
                    'row_info': {
                        'start_row': start_row,
                        'end_row': start_row + len(values) - 1,
                        'total_rows': len(values) - 1  # Excluding header row
                    }
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
        except Exception as e:
            raise Exception(f"Error reading Excel from Drive: {str(e)}")

    def _write_excel_to_drive(self, file_id, range_name, data):
        # First download the current file
        excel_content = self._get_drive_file(file_id)
        
        # Load and modify the workbook
        wb = load_workbook(io.BytesIO(excel_content))
        sheet_name, start_cell, end_cell = self._parse_range(range_name)
        
        # Create sheet if it doesn't exist
        if sheet_name not in wb.sheetnames:
            ws = wb.create_sheet(sheet_name)
        else:
            ws = wb[sheet_name]

        # Write data
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                cell = ws.cell(row=ws[start_cell].row + i, 
                             column=ws[start_cell].column + j)
                cell.value = value

        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Upload back to Drive
        self._update_drive_file(file_id, output.getvalue())
        return {'response': {'updatedRange': range_name}}

    def _read_excel_local(self, file_path, range_name):
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=range_name.split('!')[0])
            
            # Convert DataFrame to list of lists
            values = [df.columns.tolist()] + df.values.tolist()
            
            # Extract headers
            headers = values[0]
            
            # Parse range to get starting row and column
            range_parts = range_name.split('!')
            if len(range_parts) > 1:
                cell_range = range_parts[1]
                start_cell = cell_range.split(':')[0]
                start_col = ord(start_cell[0].upper()) - ord('A')
                start_row = int(''.join(filter(str.isdigit, start_cell)))
            else:
                start_col = 0
                start_row = 1

            # Create structured data with coordinates
            structured_values = []
            for row_idx, row in enumerate(values[1:], start=start_row + 1):
                row_data = {}
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row):
                        value = row[col_idx]
                        row_data[header] = {
                            'value': value,
                            'location': {
                                'row': row_idx,
                                'column': chr(ord('A') + col_idx + start_col),
                                'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                            }
                        }
                    else:
                        row_data[header] = {
                            'value': None,
                            'location': {
                                'row': row_idx,
                                'column': chr(ord('A') + col_idx + start_col),
                                'cell': f"{chr(ord('A') + col_idx + start_col)}{row_idx}"
                            }
                        }
                structured_values.append(row_data)

            return {
                'values': values,
                'structured_values': structured_values,
                'headers': headers,
                'row_info': {
                    'start_row': start_row,
                    'end_row': start_row + len(values) - 1,
                    'total_rows': len(values) - 1  # Excluding header row
                }
            }
        except Exception as e:
            raise Exception(f"Error reading local Excel file: {str(e)}")

    def _write_excel_local(self, file_path, range_name, data):
        sheet_name, start_cell, end_cell = self._parse_range(range_name)
        
        if not os.path.exists(file_path):
            wb = Workbook()
        else:
            wb = load_workbook(file_path)
        
        if sheet_name not in wb.sheetnames:
            ws = wb.create_sheet(sheet_name)
        else:
            ws = wb[sheet_name]

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                cell = ws.cell(row=ws[start_cell].row + i, 
                             column=ws[start_cell].column + j)
                cell.value = value

        wb.save(file_path)
        return {'response': {'updatedRange': range_name}}

    def update_cells(self, file_id, updates, sheet_name='Sheet1'):
        """
        Update multiple cells in a single API call.
        
        Args:
            file_id: The spreadsheet ID or path
            updates: List of dictionaries with cell coordinates and values
                   e.g., [
                       {'row': 2, 'column': 'B', 'value': 'Value 1'},
                       {'row': 5, 'column': 'C', 'value': 'Value 2'},
                       {'row': 10, 'column': 'A', 'value': 'Value 3'}
                   ]
            sheet_name: Name of the sheet to update (default: 'Sheet1')
        
        Returns:
            Dictionary with results of the update
        """
        if self._is_google_sheets(file_id):
            return self._update_cells_google_sheets(file_id, updates, sheet_name)
        else:
            return self._update_cells_excel(file_id, updates, sheet_name)

    def _update_cells_google_sheets(self, file_id, updates, sheet_name):
        # Prepare the batch update request
        data = {
            'valueInputOption': 'RAW',
            'data': [
                {
                    'range': f'{sheet_name}!{update["column"]}{update["row"]}',
                    'values': [[update['value']]]
                }
                for update in updates
            ]
        }

        url = f'https://sheets.googleapis.com/v4/spreadsheets/{file_id}/values:batchUpdate'
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return {
                'response': response.json(),
                'updates': [
                    {
                        'row': update['row'],
                        'column': update['column'],
                        'value': update['value']
                    }
                    for update in updates
                ]
            }
        else:
            response.raise_for_status()

    def _update_cells_excel(self, file_id, updates, sheet_name):
        if self._is_excel_in_drive(file_id):
            # Download current file
            excel_content = self._get_drive_file(file_id)
            wb = load_workbook(io.BytesIO(excel_content))
        else:
            if not os.path.exists(file_id):
                wb = Workbook()
            else:
                wb = load_workbook(file_id)

        # Get or create sheet
        if sheet_name not in wb.sheetnames:
            ws = wb.create_sheet(sheet_name)
        else:
            ws = wb[sheet_name]

        # Update cells
        for update in updates:
            cell = ws[f"{update['column']}{update['row']}"]
            cell.value = update['value']

        # Save changes
        if self._is_excel_in_drive(file_id):
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            self._update_drive_file(file_id, output.getvalue())
        else:
            wb.save(file_id)

        return {
            'updates': [
                {
                    'row': update['row'],
                    'column': update['column'],
                    'value': update['value']
                }
                for update in updates
            ]
        }

    def update_row_by_column_value(self, spreadsheet_id, search_column, search_value, updates):
        """
        Update a row by finding a specific value in a column.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            search_column: The column to search in (e.g., 'A', 'B', 'Name', etc.)
            search_value: The value to search for
            updates: Dictionary of column-value pairs to update (e.g., {'Age': 30, 'City': 'New York'})
        
        Returns:
            Dictionary with update information
        """
        try:
            # First, read the data to find the row
            result = self.read(spreadsheet_id, 'A1:Z1000')  # Adjust range as needed
            structured_data = result['response']['structured_values']
            
            # Find the row with matching value
            target_row = None
            for row_data in structured_data:
                # Handle both column letter and header name
                if isinstance(search_column, str) and search_column.isalpha():
                    column_key = list(row_data.keys())[ord(search_column.upper()) - ord('A')]
                else:
                    column_key = search_column
                
                if row_data[column_key]['value'] == search_value:
                    target_row = row_data
                    break
            
            if not target_row:
                raise Exception(f"No row found with {search_column} = {search_value}")
            
            # Prepare the updates
            cell_updates = []
            for column, value in updates.items():
                # Handle both column letter and header name
                if isinstance(column, str) and column.isalpha():
                    column_key = list(target_row.keys())[ord(column.upper()) - ord('A')]
                else:
                    column_key = column
                
                cell_location = target_row[column_key]['location']
                cell_updates.append({
                    'row': cell_location['row'],
                    'column': cell_location['column'],
                    'value': value
                })
            
            # Perform the updates
            return self.update_cells(spreadsheet_id, cell_updates)
            
        except Exception as e:
            raise Exception(f"Error updating row: {str(e)}")

def handler(inputs):
    file_id = inputs.get('spreadsheet_id')
    range_name = inputs.get('range')
    oauth_token = inputs.get('oauth_token')
    data = inputs.get('data')
    cell_updates = inputs.get('cell_updates')  # New parameter for multiple cell updates

    client = SpreadsheetClient(oauth_token)
    
    if cell_updates:
        return client.update_cells(file_id, cell_updates)
    elif data:
        return client.write(file_id, range_name, data)
    else:
        return client.read(file_id, range_name)

# Example usage:
# For Google Sheets:
# inputs = {
#     'spreadsheet_id': 'your_spreadsheet_id',
#     'range': 'Sheet1!A1:B2',
#     'oauth_token': 'your_oauth_token',
#     'data': [['A', 'B'], ['C', 'D']]
# }
# 
# For Excel files in Google Drive (with path):
# inputs = {
#     'spreadsheet_id': 'folder/subfolder/file.xlsx',
#     'range': 'Sheet1!A1:B2',
#     'oauth_token': 'your_oauth_token',
#     'data': [['A', 'B'], ['C', 'D']]
# }
# 
# For local Excel files:
# inputs = {
#     'spreadsheet_id': 'path/to/file.xlsx',
#     'range': 'Sheet1!A1:B2',
#     'data': [['A', 'B'], ['C', 'D']]
# }
#
# To update multiple cells in different locations:
# inputs = {
#     'spreadsheet_id': 'folder/subfolder/file.xlsx',
#     'oauth_token': 'your_oauth_token',
#     'cell_updates': [
#         {'row': 2, 'column': 'B', 'value': 'Value 1'},
#         {'row': 5, 'column': 'C', 'value': 'Value 2'},
#         {'row': 10, 'column': 'A', 'value': 'Value 3'}
#     ]
# }
#
# Example response with structured data:
# {
#     'response': {
#         'values': [
#             ['Name', 'Age', 'City'],  # Headers
#             ['John', 30, 'New York'],
#             ['Alice', 25, 'London']
#         ],
#         'structured_values': [
#             {
#                 'Name': 'John',
#                 'Age': 30,
#                 'City': 'New York'
#             },
#             {
#                 'Name': 'Alice',
#                 'Age': 25,
#                 'City': 'London'
#             }
#         ],
#         'headers': ['Name', 'Age', 'City'],
#         'row_info': {
#             'start_row': 1,
#             'end_row': 3,
#             'total_rows': 2
#         }
#     }
# }

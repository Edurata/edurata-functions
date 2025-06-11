import unittest
from index import SpreadsheetClient, handler
import os
import json
import tempfile
import shutil
from openpyxl import Workbook, load_workbook
from unittest.mock import patch, MagicMock
import requests

class TestSpreadsheetClient(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files in a local tmp directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'tmp', 'test_files')
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file_path = os.path.join(self.test_dir, 'test_file.xlsx')
        
        # Create a test workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'Sheet1'
        wb.save(self.test_file_path)
        
        # Set up test OAuth token and Drive file ID
        self.oauth_token = os.environ.get('GOOGLE_OAUTH_TOKEN', 'test_oauth_token')
        print(f"\nUsing OAuth token: {self.oauth_token[:10]}...")  # Only show first 10 chars for security
        self.drive_file_id = '12345678901234567890123456789012345678901234'  # 44 chars
        self.sheets_id = '12345678901234567890123456789012345678901234'  # 44 chars
        
        # Initialize client with OAuth token
        self.client = SpreadsheetClient(oauth_token=self.oauth_token)

    def tearDown(self):
        # Clean up temporary files using shutil.rmtree
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('requests.get')
    def test_google_sheets_operations(self, mock_get):
        """Test operations with Google Sheets"""
        # Mock Google Sheets API responses
        mock_get.return_value.json.return_value = {
            'values': [
                ['Header 1', 'Header 2'],
                ['Data 1', 'Data 2']
            ]
        }
        mock_get.return_value.status_code = 200
        
        # Test reading from Google Sheets
        inputs = {
            'spreadsheet_id': self.sheets_id,
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        
        # Verify response structure
        self.assertIn('structured_values', result)
        self.assertIn('headers', result)
        self.assertIn('row_info', result)
        
        # Test writing to Google Sheets
        inputs = {
            'spreadsheet_id': self.sheets_id,
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']],
            'oauth_token': self.oauth_token
        }
        with patch('requests.put') as mock_put:
            mock_put.return_value.json.return_value = {'updatedRange': 'Sheet1!A1:B2'}
            mock_put.return_value.status_code = 200
            result = handler(inputs)
            
            # Verify update response
            self.assertIn('updatedRange', result)

    @patch('requests.get')
    @patch('requests.patch')
    @patch('requests.put')
    def test_drive_excel_operations(self, mock_put, mock_patch, mock_get):
        """Test operations with Excel files in Google Drive"""
        # Mock Drive API responses
        mock_get.return_value.content = b'test content'
        mock_get.return_value.status_code = 200
        
        mock_patch.return_value.json.return_value = {'id': self.drive_file_id}
        mock_patch.return_value.status_code = 200
        mock_put.return_value.json.return_value = {'updatedRange': 'Sheet1!A1:B2'}
        mock_put.return_value.status_code = 200
        
        # Test reading from Drive Excel
        inputs = {
            'spreadsheet_id': self.drive_file_id,
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        
        # Verify response structure
        self.assertIn('structured_values', result)
        self.assertIn('headers', result)
        self.assertIn('row_info', result)
        
        # Test writing to Drive Excel
        inputs = {
            'spreadsheet_id': self.drive_file_id,
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']],
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        
        # Verify update response
        self.assertIn('updatedRange', result)

    def test_local_excel_operations(self):
        """Test operations with local Excel files"""
        # Test reading from local Excel
        inputs = {
            'spreadsheet_id': self.test_file_path,
            'range': 'Sheet1!A1:B2'
        }
        result = handler(inputs)
        
        # Verify response structure
        self.assertIn('structured_values', result)
        self.assertIn('headers', result)
        self.assertIn('row_info', result)
        
        # Test writing to local Excel
        inputs = {
            'spreadsheet_id': self.test_file_path,
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']]
        }
        result = handler(inputs)
        
        # Verify update response
        self.assertIn('updates', result)

    @patch('requests.get')
    def test_file_type_detection(self, mock_get):
        """Test detection of different file types"""
        # Simulate a successful response for Google Sheets and Drive file type detection
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        # Test Google Sheets detection
        self.assertTrue(self.client._is_google_sheets('https://docs.google.com/spreadsheets/d/12345678901234567890123456789012345678901234'))
        self.assertTrue(self.client._is_google_sheets('12345678901234567890123456789012345678901234'))
        # Test Drive Excel detection
        self.assertTrue(self.client._is_excel_in_drive('12345678901234567890123456789012345678901234'))
        # Test local file detection
        local_path = os.path.join(self.test_dir, 'test_local_file.xlsx')
        self.assertTrue(self.client._is_local_file(self.test_file_path))
        self.assertTrue(self.client._is_local_file(local_path))

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test error handling for various scenarios"""
        # Mock API error
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = Exception('Not found')
        
        # Test with invalid Drive file
        inputs = {
            'spreadsheet_id': 'invalid_drive_id',
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        with self.assertRaises(Exception):
            handler(inputs)
        
        # Test with invalid local file
        nonexistent_file = os.path.join(self.test_dir, 'nonexistent.xlsx')
        inputs = {
            'spreadsheet_id': nonexistent_file,
            'range': 'Sheet1!A1:B2'
        }
        with self.assertRaises(Exception):
            handler(inputs)

    @patch('requests.get')
    def test_drive_api_calls(self, mock_get):
        """Test that Google Drive API calls are made correctly when using a Drive file ID."""
        # Mock Drive API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        # Use a Drive file ID
        drive_id = '12345678901234567890123456789012345678901234'
        self.assertTrue(self.client._is_excel_in_drive(drive_id))
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_with(
            f'https://www.googleapis.com/drive/v3/files/{drive_id}',
            headers={'Authorization': f'Bearer {self.oauth_token}', 'Content-Type': 'application/json'}
        )

    def test_real_cloud_operations(self):
        """Test operations on a real spreadsheet in Google Drive"""
        # Create a new Google Sheet using only the spreadsheets API
        inputs = {
            'spreadsheet_id': 'new_google_sheet',
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']],
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        self.assertIn('spreadsheetId', result)
        self.assertIn('spreadsheetUrl', result)
        spreadsheet_id = result['spreadsheetId']
        spreadsheet_url = result['spreadsheetUrl']
        print(f"\nCreated Google Sheet: {spreadsheet_url}")
        
        # Read back
        inputs = {
            'spreadsheet_id': spreadsheet_id,
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        self.assertIn('structured_values', result)
        self.assertEqual(result['structured_values'][0]['Header 1'], 'Data 1')
        self.assertEqual(result['structured_values'][0]['Header 2'], 'Data 2')
        
        # Note: We can't delete the spreadsheet with drive.file scope
        # The user will need to delete it manually from their Drive
        print(f"\nTest completed. Please delete the spreadsheet manually: {spreadsheet_url}")

    def test_create_new_local_excel(self):
        """Test creating a new local Excel file if not present and writing/reading data."""
        new_file = os.path.join(self.test_dir, 'new_file.xlsx')
        # Write to new file
        inputs = {
            'spreadsheet_id': new_file,
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']],
            'oauth_token': None  # Explicitly set to None for local operations
        }
        result = handler(inputs)
        self.assertIn('created', result)
        # Read back
        inputs = {
            'spreadsheet_id': new_file,
            'range': 'Sheet1!A1:B2',
            'oauth_token': None  # Explicitly set to None for local operations
        }
        result = handler(inputs)
        self.assertIn('structured_values', result)
        self.assertEqual(result['structured_values'][0]['Header 1'], 'Data 1')
        self.assertEqual(result['structured_values'][0]['Header 2'], 'Data 2')

    def test_create_new_google_sheet(self):
        """Test creating a new Google Sheet if not present and writing/reading data."""
        # Create new Google Sheet
        inputs = {
            'spreadsheet_id': 'new_google_sheet',
            'range': 'Sheet1!A1:B2',
            'values': [['Header 1', 'Header 2'], ['Data 1', 'Data 2']],
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        self.assertIn('spreadsheetId', result)
        self.assertIn('spreadsheetUrl', result)
        print(f"\nCreated Google Sheet: {result['spreadsheetUrl']}")
        # Read back
        inputs = {
            'spreadsheet_id': result['spreadsheetId'],
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        self.assertIn('structured_values', result)
        self.assertEqual(result['structured_values'][0]['Header 1'], 'Data 1')
        self.assertEqual(result['structured_values'][0]['Header 2'], 'Data 2')

    @patch('requests.get')
    def test_unauthorized_access_logs_open_with_app_link(self, mock_get):
        """Test that unauthorized access logs the 'Open with app' link."""
        # Simulate an unauthorized response
        mock_get.return_value.status_code = 403
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_get.return_value)

        file_id = '12345678901234567890123456789012345678901234'
        with self.assertRaises(Exception):
            self.client._read_google_sheets(file_id, 'Sheet1!A1:B2')

        # Check if the log contains the correct URL
        app_id = "YOUR_OAUTH_CLIENT_ID"  # Replace with your actual OAuth client ID
        expected_url = f"https://docs.google.com/spreadsheets/d/{file_id}/open?usp=drive_sdk&appId={app_id}"
        with self.assertLogs(level='INFO') as log:
            self.client._log_open_with_app_link(file_id)
            self.assertIn(expected_url, log.output[0])

if __name__ == '__main__':
    unittest.main()

# Example usage scenarios:
"""
1. Reading data with structured format:
inputs = {
    'spreadsheet_id': 'your_spreadsheet_id',
    'range': 'Sheet1!A1:C3',
    'oauth_token': 'your_oauth_token'
}
result = handler(inputs)
# Access structured data
structured_data = result['response']['structured_values']
# Filter data
filtered_data = [row for row in structured_data if row['Age'] > 25]

2. Updating multiple cells:
inputs = {
    'spreadsheet_id': 'your_spreadsheet_id',
    'oauth_token': 'your_oauth_token',
    'cell_updates': [
        {'row': 2, 'column': 'B', 'value': 'Value 1'},
        {'row': 3, 'column': 'C', 'value': 'Value 2'},
        {'row': 4, 'column': 'A', 'value': 'Value 3'}
    ]
}
result = handler(inputs)

3. Creating and updating a new file:
inputs = {
    'spreadsheet_id': 'folder/subfolder/new_file.xlsx',
    'oauth_token': 'your_oauth_token',
    'cell_updates': [
        {'row': 1, 'column': 'A', 'value': 'Header 1'},
        {'row': 1, 'column': 'B', 'value': 'Header 2'},
        {'row': 2, 'column': 'A', 'value': 'Data 1'},
        {'row': 2, 'column': 'B', 'value': 'Data 2'}
    ]
}
result = handler(inputs)

4. Reading and filtering data:
inputs = {
    'spreadsheet_id': 'your_spreadsheet_id',
    'range': 'Sheet1!A1:C10',
    'oauth_token': 'your_oauth_token'
}
result = handler(inputs)
structured_data = result['response']['structured_values']
# Filter by multiple conditions
filtered_data = [
    row for row in structured_data 
    if row['Age'] > 25 and row['City'] == 'New York'
]

# Update user information by email
inputs = {
    'spreadsheet_id': 'your_spreadsheet_id',
    'oauth_token': 'your_oauth_token',
    'search_column': 'Email',  # Column to search in
    'search_value': 'john@example.com',  # Value to find
    'updates': {  # Fields to update
        'Age': '31',
        'City': 'Boston'
    }
}
result = handler(inputs)

# Update using column letters
inputs = {
    'spreadsheet_id': 'your_spreadsheet_id',
    'oauth_token': 'your_oauth_token',
    'search_column': 'A',  # First column
    'search_value': 'john@example.com',
    'updates': {
        'C': '31',  # Third column
        'D': 'Boston'  # Fourth column
    }
}
result = handler(inputs)
""" 
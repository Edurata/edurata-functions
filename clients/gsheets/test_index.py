import unittest
from index import SpreadsheetClient, handler
import os
import json

class TestSpreadsheetClient(unittest.TestCase):
    def setUp(self):
        # You'll need to set these environment variables or replace with actual values
        self.oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')
        self.spreadsheet_id = os.getenv('TEST_SPREADSHEET_ID')
        self.client = SpreadsheetClient(self.oauth_token)

    def test_read_structured_data(self):
        """Test reading data with structured format"""
        inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'range': 'Sheet1!A1:C3',  # Assuming headers and 2 rows of data
            'oauth_token': self.oauth_token
        }
        result = handler(inputs)
        
        # Verify response structure
        self.assertIn('response', result)
        self.assertIn('structured_values', result['response'])
        self.assertIn('headers', result['response'])
        self.assertIn('row_info', result['response'])
        
        # Verify data structure
        structured_data = result['response']['structured_values']
        self.assertTrue(isinstance(structured_data, list))
        if structured_data:
            self.assertTrue(isinstance(structured_data[0], dict))
            self.assertEqual(set(structured_data[0].keys()), set(result['response']['headers']))

    def test_update_multiple_cells(self):
        """Test updating multiple cells in different locations"""
        inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'cell_updates': [
                {'row': 2, 'column': 'B', 'value': 'Test Value 1'},
                {'row': 3, 'column': 'C', 'value': 'Test Value 2'},
                {'row': 4, 'column': 'A', 'value': 'Test Value 3'}
            ]
        }
        result = handler(inputs)
        
        # Verify update response
        self.assertIn('updates', result)
        self.assertEqual(len(result['updates']), 3)
        
        # Verify each update
        for update in result['updates']:
            self.assertIn('row', update)
            self.assertIn('column', update)
            self.assertIn('value', update)

    def test_create_and_update_file(self):
        """Test creating a new file and updating it"""
        test_file_path = 'test_folder/test_file.xlsx'
        inputs = {
            'spreadsheet_id': test_file_path,
            'oauth_token': self.oauth_token,
            'cell_updates': [
                {'row': 1, 'column': 'A', 'value': 'Header 1'},
                {'row': 1, 'column': 'B', 'value': 'Header 2'},
                {'row': 2, 'column': 'A', 'value': 'Data 1'},
                {'row': 2, 'column': 'B', 'value': 'Data 2'}
            ]
        }
        
        # Create and update file
        result = handler(inputs)
        self.assertIn('updates', result)
        
        # Read the created file
        read_inputs = {
            'spreadsheet_id': test_file_path,
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        read_result = handler(read_inputs)
        
        # Verify the data
        self.assertIn('response', read_result)
        self.assertIn('structured_values', read_result['response'])
        structured_data = read_result['response']['structured_values']
        self.assertEqual(len(structured_data), 1)  # One row of data (excluding header)
        self.assertEqual(structured_data[0]['Header 1'], 'Data 1')
        self.assertEqual(structured_data[0]['Header 2'], 'Data 2')

    def test_read_with_filters(self):
        """Test reading data with specific filters"""
        # First, set up some test data
        setup_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'cell_updates': [
                {'row': 1, 'column': 'A', 'value': 'Name'},
                {'row': 1, 'column': 'B', 'value': 'Age'},
                {'row': 1, 'column': 'C', 'value': 'City'},
                {'row': 2, 'column': 'A', 'value': 'John'},
                {'row': 2, 'column': 'B', 'value': '30'},
                {'row': 2, 'column': 'C', 'value': 'New York'},
                {'row': 3, 'column': 'A', 'value': 'Alice'},
                {'row': 3, 'column': 'B', 'value': '25'},
                {'row': 3, 'column': 'C', 'value': 'London'}
            ]
        }
        handler(setup_inputs)
        
        # Read the data
        read_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'range': 'Sheet1!A1:C3',
            'oauth_token': self.oauth_token
        }
        result = handler(read_inputs)
        
        # Verify the structured data
        structured_data = result['response']['structured_values']
        self.assertEqual(len(structured_data), 2)  # Two rows of data
        
        # Example of filtering the data (in your application code)
        filtered_data = [row for row in structured_data if row['Age'] == '30']
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]['Name'], 'John')

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test with invalid range
        inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'range': 'InvalidRange',
            'oauth_token': self.oauth_token
        }
        with self.assertRaises(Exception):
            handler(inputs)
        
        # Test with invalid file path
        inputs = {
            'spreadsheet_id': 'nonexistent/path/file.xlsx',
            'range': 'Sheet1!A1:B2',
            'oauth_token': self.oauth_token
        }
        with self.assertRaises(Exception):
            handler(inputs)

    def test_update_row_by_column_value(self):
        """Test updating a row by finding a value in a specific column"""
        # First, set up test data
        setup_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'cell_updates': [
                {'row': 1, 'column': 'A', 'value': 'Email'},
                {'row': 1, 'column': 'B', 'value': 'Name'},
                {'row': 1, 'column': 'C', 'value': 'Age'},
                {'row': 1, 'column': 'D', 'value': 'City'},
                {'row': 2, 'column': 'A', 'value': 'john@example.com'},
                {'row': 2, 'column': 'B', 'value': 'John Doe'},
                {'row': 2, 'column': 'C', 'value': '30'},
                {'row': 2, 'column': 'D', 'value': 'New York'},
                {'row': 3, 'column': 'A', 'value': 'alice@example.com'},
                {'row': 3, 'column': 'B', 'value': 'Alice Smith'},
                {'row': 3, 'column': 'C', 'value': '25'},
                {'row': 3, 'column': 'D', 'value': 'London'}
            ]
        }
        handler(setup_inputs)

        # Test updating by column name
        update_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'search_column': 'Email',
            'search_value': 'john@example.com',
            'updates': {
                'Age': '31',
                'City': 'Boston'
            }
        }
        result = handler(update_inputs)
        
        # Verify the update
        self.assertIn('updates', result)
        self.assertEqual(len(result['updates']), 2)  # Two cells updated
        
        # Read back the data to verify changes
        read_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'range': 'Sheet1!A1:D3',
            'oauth_token': self.oauth_token
        }
        read_result = handler(read_inputs)
        structured_data = read_result['response']['structured_values']
        
        # Find the updated row
        updated_row = None
        for row in structured_data:
            if row['Email']['value'] == 'john@example.com':
                updated_row = row
                break
        
        # Verify the updates
        self.assertIsNotNone(updated_row)
        self.assertEqual(updated_row['Age']['value'], '31')
        self.assertEqual(updated_row['City']['value'], 'Boston')
        
        # Test updating by column letter
        update_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'search_column': 'A',  # Email column
            'search_value': 'alice@example.com',
            'updates': {
                'C': '26',  # Age column
                'D': 'Paris'  # City column
            }
        }
        result = handler(update_inputs)
        
        # Verify the update
        self.assertIn('updates', result)
        self.assertEqual(len(result['updates']), 2)
        
        # Read back the data to verify changes
        read_result = handler(read_inputs)
        structured_data = read_result['response']['structured_values']
        
        # Find the updated row
        updated_row = None
        for row in structured_data:
            if row['Email']['value'] == 'alice@example.com':
                updated_row = row
                break
        
        # Verify the updates
        self.assertIsNotNone(updated_row)
        self.assertEqual(updated_row['Age']['value'], '26')
        self.assertEqual(updated_row['City']['value'], 'Paris')
        
        # Test error handling - non-existent value
        update_inputs = {
            'spreadsheet_id': self.spreadsheet_id,
            'oauth_token': self.oauth_token,
            'search_column': 'Email',
            'search_value': 'nonexistent@example.com',
            'updates': {
                'Age': '35',
                'City': 'Tokyo'
            }
        }
        with self.assertRaises(Exception):
            handler(update_inputs)

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
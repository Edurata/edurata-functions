from index import handler  # Adjust the import path based on your file structure
import unittest
import os
import json
mock_event = {
    'sender': os.environ['SENDER'],
    'to': os.environ['SENDER'],
    'subject': '',
    'body': '',
}

class MyTestCase(unittest.TestCase):
    def test_my_function(self):
        # raise Exception('required inputs not present')
        response = handler(mock_event)
        print(response)
        # raise Exception(response)
        self.assertIsNot(response, False)

if __name__ == '__main__':
    unittest.main()

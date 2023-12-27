import unittest
from unittest.mock import patch, MagicMock
import os
import index

class TestIndex(unittest.TestCase):

    @patch('index.tweepy.OAuthHandler')
    @patch('index.tweepy.API')
    def test_api(self, mock_api, mock_auth):
        # get credentials from json file
        if os.path.exists('credentials.json'):
            with open('credentials.json') as file:
                credentials = json.load(file)
                os.environ['API_KEY'] = credentials['TWITTER_API_KEY']
                os.environ['API_SECRET'] = credentials['TWITTER_API_SECRET']
                os.environ['ACCESS_TOKEN'] = credentials['TWITTER_ACCESS_TOKEN']
                os.environ['ACCESS_TOKEN_SECRET'] = credentials['TWITTER_ACCESS_TOKEN_SECRET']

        mock_auth_instance = mock_auth.return_value
        mock_auth_instance.set_access_token.return_value = None
        mock_api.return_value = 'client'

        result = index.api()
        self.assertEqual(result, 'client')

    @patch('index.tweet')
    def test_handler(self, mock_tweet):
        inputs = MagicMock()
        inputs.messages = {'key1': 'message1', 'key2': 'message2'}
        inputs.mediaPaths = {'key1': 'path1', 'key2': 'path2'}

        index.handler(inputs)
        mock_tweet.assert_any_call('message1', 'path1')
        mock_tweet.assert_any_call('message2', 'path2')

if __name__ == '__main__':
    unittest.main()
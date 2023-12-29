import unittest
import index

class TestIndex(unittest.TestCase):

    def test_get_posts(self):
        # Run the function
        channel_name = 'knVknVknV'
        inputs = {
            'channelId': channel_name,
            'sinceDays': 3,
            'imageDir': 'downloaded_images'
        }
        return_object = index.handler(inputs)
        # Check that the function returns a list
        self.assertIsInstance(return_object["posts"], list)

        # Check that each item in the list is a Message
        for post in return_object["posts"]:
            # Check if the post has an id and text attribute
            self.assertTrue(hasattr(post, 'id'))
            self.assertTrue(hasattr(post, 'text'))

if __name__ == '__main__':
    unittest.main()
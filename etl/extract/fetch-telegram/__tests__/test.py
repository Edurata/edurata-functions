import unittest
import index
import asyncio

class TestIndex(unittest.TestCase):

    def test_get_posts(self):
        # Run the function
        channel_name = 'knVknVknV'
        loop = asyncio.get_event_loop()
        inputs = {
            'channel_name': channel_name
        }
        posts = loop.run_until_complete(index.handler(inputs))
        # Check that the function returns a list
        self.assertIsInstance(posts, list)

        # Check that each item in the list is a Message
        for post in posts:
            # Check if the post has an id and text attribute
            self.assertTrue(hasattr(post, 'id'))
            self.assertTrue(hasattr(post, 'text'))

if __name__ == '__main__':
    unittest.main()
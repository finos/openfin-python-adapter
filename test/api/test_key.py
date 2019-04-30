from openfin import SubKey
import unittest

class SubKeyTests(unittest.TestCase):

    def test_from_string(self):
        self.assertEqual(SubKey.from_string(None), SubKey())
        self.assertEqual(SubKey.from_string("hello"), SubKey(topic="hello"))

        self.assertEqual(SubKey.from_string(SubKey(topic="hello")), SubKey(topic="hello"))
        self.assertEqual(SubKey.from_string(SubKey(name="hello")), SubKey(name="hello"))
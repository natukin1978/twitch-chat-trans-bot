import unittest

from config_helper import readConfig


class TestConfigHelper(unittest.TestCase):
    def test_readConfig(self):
        expected = {
          "a": 1,
          "b": "2",
          "c": False,
        }
        actual = readConfig("test_data/test_config_helper.json")
        self.assertEqual(expected, actual)

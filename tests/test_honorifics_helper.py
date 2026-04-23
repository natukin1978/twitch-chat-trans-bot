import unittest

from honorifics_helper import add_honorifics, read_honorifics


class TestExcludeWordsHelper(unittest.TestCase):
    def test_read_honorifics_file_not_found(self):
        actual = read_honorifics()  # わざと存在しないファイルを指定
        self.assertEqual({}, actual)

    def test_read_honorifics(self):
        actual = read_honorifics("test_data/honorifics.json")
        self.assertEqual({'default': 'さん', 'other': ['ちゃん', 'さま', 'くん']}, actual)

    def test_add_honorifics(self):
        honorifics = {'default': 'さん', 'other': ['ちゃん', 'さま', 'くん']}
        self.assertEqual("ナツキさん", add_honorifics(honorifics, "ナツキ"))
        self.assertEqual("ナツキさん", add_honorifics(honorifics, "ナツキさん"))
        self.assertEqual("ナツキちゃん", add_honorifics(honorifics, "ナツキちゃん"))


import unittest

from replace_words_helper import match_replace_word, read_replace_words


class TestExcludeWordsHelper(unittest.TestCase):
    def test_read_replace_words_file_not_found(self):
        actual = read_replace_words()  # わざと存在しないファイルを指定
        self.assertEqual({}, actual)

    def test_read_replace_words(self):
        actual = read_replace_words("test_data/replace_words.json")
        self.assertEqual([{'from': '888+', 'to': 'ぱちぱちぱち'}], actual)

    def test_match_replace_word_888(self):
        replace_words = [{'from': '888+', 'to': 'ぱちぱちぱち'}]
        self.assertEqual("", match_replace_word(replace_words, ""))
        self.assertEqual("8", match_replace_word(replace_words, "8"))
        self.assertEqual("88", match_replace_word(replace_words, "88"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "888"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "8888"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "88888"))
        self.assertEqual("ぱちぱちぱち円", match_replace_word(replace_words, "888円"))
        self.assertEqual("ぱちぱちぱちすごーい", match_replace_word(replace_words, "8888すごーい"))

    def test_match_replace_word_kusa(self):
        replace_words = [{'from': '(?<![a-zA-Z])w+(?![a-zA-Z])', 'to': '草'}]
        self.assertEqual("", match_replace_word(replace_words, ""))
        self.assertEqual("PewPewPew", match_replace_word(replace_words, "PewPewPew"))
        self.assertEqual("草", match_replace_word(replace_words, "www"))
        self.assertEqual("辛辣で草", match_replace_word(replace_words, "辛辣でw"))
        self.assertEqual("lol 草", match_replace_word(replace_words, "lol www"))

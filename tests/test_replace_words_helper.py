import unittest

from replace_words_helper import match_replace_word, read_replace_words


class TestExcludeWordsHelper(unittest.TestCase):
    def test_read_replace_words_file_not_found(self):
        actual = read_replace_words()  # わざと存在しないファイルを指定
        self.assertEqual({}, actual)

    def test_read_replace_words(self):
        actual = read_replace_words("test_data/replace_words.csv")
        self.assertEqual([["888+", "ぱちぱちぱち"]], actual)

    def test_match_replace_word_888(self):
        replace_words = [["888+", "ぱちぱちぱち"]]
        self.assertEqual("", match_replace_word(replace_words, ""))
        self.assertEqual("8", match_replace_word(replace_words, "8"))
        self.assertEqual("88", match_replace_word(replace_words, "88"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "888"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "8888"))
        self.assertEqual("ぱちぱちぱち", match_replace_word(replace_words, "88888"))
        self.assertEqual("888円", match_replace_word(replace_words, "888円"))

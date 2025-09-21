import unittest

from exclude_words_helper import match_exclude_word, read_exclude_words


class TestExcludeWordsHelper(unittest.TestCase):
    def test_read_exclude_words_file_not_found(self):
        actual = read_exclude_words()  # わざと存在しないファイルを指定
        self.assertEqual([], actual)

    def test_match_exclude_word_gg(self):
        exclude_words = ["gg"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertFalse(match_exclude_word(exclude_words, "g"))
        self.assertFalse(match_exclude_word(exclude_words, "G"))
        self.assertTrue(match_exclude_word(exclude_words, "gg"))
        self.assertTrue(match_exclude_word(exclude_words, "GG"))
        self.assertFalse(match_exclude_word(exclude_words, "ggg"))
        self.assertFalse(match_exclude_word(exclude_words, "GGG"))

    def test_match_exclude_word_gg_zenkaku(self):
        exclude_words = ["gg"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertFalse(match_exclude_word(exclude_words, "ｇ"))
        self.assertFalse(match_exclude_word(exclude_words, "Ｇ"))
        self.assertTrue(match_exclude_word(exclude_words, "ｇｇ"))
        self.assertTrue(match_exclude_word(exclude_words, "ＧＧ"))
        self.assertFalse(match_exclude_word(exclude_words, "ｇｇｇ"))
        self.assertFalse(match_exclude_word(exclude_words, "ＧＧＧ"))

    def test_match_exclude_word_ok(self):
        exclude_words = ["ok.?"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertFalse(match_exclude_word(exclude_words, "o"))
        self.assertFalse(match_exclude_word(exclude_words, "k"))
        self.assertTrue(match_exclude_word(exclude_words, "ok"))
        self.assertTrue(match_exclude_word(exclude_words, "OK"))
        self.assertTrue(match_exclude_word(exclude_words, "ok."))
        self.assertTrue(match_exclude_word(exclude_words, "OK."))
        self.assertFalse(match_exclude_word(exclude_words, "ok desu"))
        self.assertFalse(match_exclude_word(exclude_words, "ok arigato"))

    def test_match_exclude_word_w(self):
        exclude_words = ["w+", "草"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertTrue(match_exclude_word(exclude_words, "w"))
        self.assertTrue(match_exclude_word(exclude_words, "ww"))
        self.assertTrue(match_exclude_word(exclude_words, "www"))
        self.assertTrue(match_exclude_word(exclude_words, "wwww"))
        self.assertTrue(match_exclude_word(exclude_words, "W"))
        self.assertTrue(match_exclude_word(exclude_words, "WW"))
        self.assertTrue(match_exclude_word(exclude_words, "WWW"))
        self.assertTrue(match_exclude_word(exclude_words, "WWWW"))
        self.assertTrue(match_exclude_word(exclude_words, "草"))
        self.assertFalse(match_exclude_word(exclude_words, "ウケるw"))

    def test_match_exclude_word_0_9(self):
        exclude_words = ["[0-9]+"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertTrue(match_exclude_word(exclude_words, "0"))
        self.assertTrue(match_exclude_word(exclude_words, "12"))
        self.assertTrue(match_exclude_word(exclude_words, "345"))
        self.assertTrue(match_exclude_word(exclude_words, "6789"))
        self.assertTrue(match_exclude_word(exclude_words, "88888"))
        self.assertFalse(match_exclude_word(exclude_words, "1番"))

    def test_match_exclude_word_0_9_zenkaku(self):
        exclude_words = ["[0-9]+"]
        self.assertFalse(match_exclude_word(exclude_words, ""))
        self.assertTrue(match_exclude_word(exclude_words, "０"))
        self.assertTrue(match_exclude_word(exclude_words, "１２"))
        self.assertTrue(match_exclude_word(exclude_words, "３４５"))
        self.assertTrue(match_exclude_word(exclude_words, "６７８９"))
        self.assertTrue(match_exclude_word(exclude_words, "８８８８８"))
        self.assertFalse(match_exclude_word(exclude_words, "１番"))

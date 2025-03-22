import unittest

from hankaku_to_zenkaku import hankaku_to_zenkaku_symbols


class TestHankakuToZenkaku(unittest.TestCase):

    def test_hankaku_to_zenkaku_symbols_empty_string(self):
        self.assertEqual("", hankaku_to_zenkaku_symbols(""))

    def test_hankaku_to_zenkaku_symbols_no_symbols(self):
        self.assertEqual("123　abc", hankaku_to_zenkaku_symbols("123 abc"))

    def test_hankaku_to_zenkaku_symbols_some_symbols(self):
        result = hankaku_to_zenkaku_symbols("&+<=>@^_`|~!#$,%.'()- ")
        self.assertEqual("＆＋＜＝＞＠＾＿｀｜～！＃＄，％．’（）－　", result)

    def test_hankaku_to_zenkaku_symbols_mixed_symbols_and_text(self):
        self.assertEqual(
            "これは＆と＋を含む文字列です。＜＝　＠　＾　＿　｀　｜　～　！　123　abc",
            hankaku_to_zenkaku_symbols(
                "これは&と+を含む文字列です。<= @ ^ _ ` | ~ ! 123 abc"
            ),
        )

    def test_hankaku_to_zenkaku_symbols_all_symbols(self):
        all_symbols = "&+<=>@^_`|~!#$,%.'()-"
        all_zenkaku_symbols = "＆＋＜＝＞＠＾＿｀｜～！＃＄，％．’（）－"
        self.assertEqual(all_zenkaku_symbols, hankaku_to_zenkaku_symbols(all_symbols))

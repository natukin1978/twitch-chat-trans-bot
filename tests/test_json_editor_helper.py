import unittest

from json_editor_helper import sort_dict_by_schema


class TestJsonEditorHelper(unittest.TestCase):
    def test_array_object_sorting(self):
        # 配列内のオブジェクトが propertyOrder 通りにソートされるか検証
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"propertyOrder": 1},
                    "cid": {"propertyOrder": 2}
                }
            }
        }

        # 初期状態ではキーの順序が逆転しているデータ
        data = [
            {"cid": 50163, "name": "電脳娘フユカ"},
            {"cid": 50401, "name": "nikuman_sub"}
        ]

        sorted_data = sort_dict_by_schema(data, schema)

        # 各要素の最初のキーが name になっていることを確認
        for item in sorted_data:
            keys = list(item.keys())
            self.assertEqual(keys[0], "name")
            self.assertEqual(keys[1], "cid")

    def test_nested_object_sorting(self):
        # 階層構造になったオブジェクトのソートを検証
        schema = {
            "type": "object",
            "properties": {
                "z": {"propertyOrder": 2},
                "a": {"propertyOrder": 1}
            }
        }
        data = {"z": 1, "a": 2}
        sorted_data = sort_dict_by_schema(data, schema)

        self.assertEqual(list(sorted_data.keys()), ["a", "z"])

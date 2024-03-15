# Copyright © 2023- Frello Technology Private Limited

from chainfury.base import get_value_by_keys

import unittest


class TestGetValueByKeys(unittest.TestCase):
    def test_00_kv(self):
        # Test with a single-level dictionary
        data = {"key": "value"}
        keys = "key"
        expected_result = "value"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_01_two_level_kv(self):
        # Test with a two-level nested dictionary
        data = {"level1": {"level2": {"level3": "Nested value"}}}
        keys = ("level1", "level2", "level3")
        expected_result = "Nested value"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_02_three_level_kv(self):
        # Test with a three-level nested dictionary
        data = {"a": {"b": {"c": {"d": "Deeply nested value"}}}}
        keys = ("a", "b", "c", "d")
        expected_result = "Deeply nested value"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_03_non_existent_key(self):
        # Test with a single-level dictionary and non-existent key
        data = {"key": "value"}
        keys = "non_existent_key"
        expected_result = None
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_04_single_level_list(self):
        # Test with a single-level list
        data = ["apple", "banana", "cherry"]
        keys = 1
        expected_result = "banana"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_05_two_level_list(self):
        # Test with a two-level nested list
        data = [["a", "b"], ["c", "d"], ["e", "f"]]
        keys = (2, 1)
        expected_result = "f"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_06_three_level_list(self):
        # Test with a three-level nested list
        data = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        keys = (0, 1, 0)
        expected_result = 3
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_07_nested_kv_list(self):
        # Test with a mixed nested dictionary and list
        data = {
            "fruits": ["apple", "banana", "cherry"],
            "numbers": {
                "even": [2, 4, 6],
                "odd": [1, 3, 5],
            },
        }
        keys = ("numbers", "even", 1)
        expected_result = 4
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_08_nested_list_kv(self):
        # Test with a dictionary containing an array (list) as a value
        data = {
            "fruits": ["apple", "banana", "cherry"],
            "numbers": [1, 2, 3, 4, 5],
            "nested": {
                "colors": ["red", "blue", "green"],
                "animals": ["cat", "dog", "elephant"],
            },
        }

        # Test with keys pointing to the array value in the dictionary
        keys = ("fruits", 1)
        expected_result = "banana"
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

        # Test with keys pointing to the nested array value in the dictionary
        keys2 = ("nested", "colors", 2)
        expected_result2 = "green"
        self.assertEqual(get_value_by_keys(data, keys2), expected_result2)

    def test_09_nested_dict_with_wildcard(self):
        # Test with a nested dictionary with a wildcard
        data = {
            "nested": [
                {"colors": ["red", "blue", "green"]},
                {"colors": ["white", "black", "grey"]},
            ]
        }
        #
        keys = ("nested", "*")
        expected_result = [
            {"colors": ["red", "blue", "green"]},
            {"colors": ["white", "black", "grey"]},
        ]
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

        #
        keys2 = ("nested", "*", "colors", 1)
        expected_result = ["blue", "black"]
        self.assertEqual(get_value_by_keys(data, keys2), expected_result)

    def test_10_multiple_wildcards(self):
        # Test with a deeply nested dictionary with multiple wildcards
        data = {
            "x": {
                "y": {"colors": ["red", "blue", "green"]},
                "z": {"colors": ["white", "black", "grey"]},
            },
            "w": {
                "p": {"colors": ["orange", "purple", "yellow"]},
            },
        }
        keys = ("x", "*", "colors", 1)
        expected_result = {"y": "blue", "z": "black"}
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_11_single_wildcard(self):
        data = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "index": 0,
                    "embedding": [
                        -0.03472504,
                        -0.025310948,
                        0.0033682163,
                        -0.0060247383,
                        -0.030130738,
                        -0.005823914,
                    ],
                }
            ],
        }
        keys = ("data", "*", "embedding")
        expected_result = [
            [
                -0.03472504,
                -0.025310948,
                0.0033682163,
                -0.0060247383,
                -0.030130738,
                -0.005823914,
            ]
        ]
        self.assertEqual(get_value_by_keys(data, keys), expected_result)

    def test_12_return(self):
        data = "hello world!"
        keys = (0,)
        self.assertEqual(get_value_by_keys(data, keys), data)


if __name__ == "__main__":
    unittest.main()

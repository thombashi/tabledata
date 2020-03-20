"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from collections import OrderedDict

from tabledata import to_value_matrix


class Test_to_value_matrix:
    def test_normal_dict_rows(self):
        expect = [
            [1, None, None],
            [None, 2.1, "hoge"],
            [0, 0.1, "foo"],
            [None, None, None],
            [-1, -0.1, "bar"],
        ]

        assert (
            to_value_matrix(
                ["A", "B", "C"],
                [
                    {"A": 1},
                    {"B": 2.1, "C": "hoge"},
                    {"A": 0, "B": 0.1, "C": "foo"},
                    {},
                    {"A": -1, "B": -0.1, "C": "bar", "D": "extra"},
                ],
            )
            == expect
        )

    def test_normal_OrderedDict_rows(self):
        expect = [
            [1, None, None],
            [None, 2.1, "hoge"],
            [0, 0.1, "foo"],
            [None, None, None],
            [-1, -0.1, "bar"],
        ]

        assert (
            to_value_matrix(
                ["A", "B", "C"],
                [
                    OrderedDict({"A": 1}),
                    OrderedDict({"B": 2.1, "C": "hoge"}),
                    OrderedDict({"A": 0, "B": 0.1, "C": "foo"}),
                    OrderedDict({}),
                    OrderedDict({"A": -1, "B": -0.1, "C": "bar", "D": "extra"}),
                ],
            )
            == expect
        )

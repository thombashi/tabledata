"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import itertools
import sys
from collections import OrderedDict, namedtuple
from decimal import Decimal

import pytest
from typepy import Integer, String

from tabledata import DataError, PatternMatch, TableData


attr_list_2 = ["attr_a", "attr_b"]

NamedTuple2 = namedtuple("NamedTuple2", " ".join(attr_list_2))


def dumps_results(expected=None, actual=None):
    try:
        from pytablewriter import dumps_tabledata
    except ImportError:
        return

    if expected:
        print("expected: {}".format(dumps_tabledata(expected)))

    if actual:
        print("actual: {}".format(dumps_tabledata(actual)))


class Test_TableData_constructor:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                TableData("normal", ["a", "b"], [[1, 2], [3, 4]]),
            ],
            ["empty_records", ["a", "b"], [], TableData("empty_records", ["a", "b"], [])],
            ["empty_header", [], [[1, 2], [3, 4]], TableData("empty_header", [], [[1, 2], [3, 4]])],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        dumps_results(expected=expected, actual=tabledata)

        assert tabledata == expected

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "none_header",
                None,
                [[1, 2], [3, 4]],
                TableData("none_header", None, [[1, 2], [3, 4]]),
            ],
            ["none_records", ["a", "b"], None, TableData("none_records", ["a", "b"], [])],
            ["none_data", None, None, TableData("none_data", [], [])],
        ],
    )
    def test_normal_with_none_value(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert tabledata == expected

    def test_normal_type_hints(self,):
        type_hints = [Integer, String]
        tabledata = TableData("type hints", ["a", "b"], [[1, 2], [1, 2]], type_hints=type_hints)

        for col_dp in tabledata.column_dp_list:
            print(col_dp)

        dumps_results(actual=tabledata)

        for row_dp in tabledata.value_dp_matrix:
            for dp, type_hint in zip(row_dp, type_hints):
                print(dp)

            assert dp.type_class == type_hint

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [["invalid_data", ["a", "b"], [1, 2], DataError]],
    )
    def test_exception(self, table_name, headers, rows, expected):
        with pytest.raises(expected):
            TableData(table_name, headers, rows).value_matrix


def yield_rows():
    rows = [[1, 2], [3, 4]]

    yield from rows


class Test_TableData_num_rows:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            ["normal", ["a", "b"], [[1, 2], [3, 4]], 2],
            ["empty", ["a", "b"], [], 0],
            ["zip", ["a", "b"], zip(["a", 1], ["b", 2]), None],
            ["empty", ["a", "b"], yield_rows(), None],
            ["empty", ["a", "b"], itertools.product([[1, 2], [3, 4]]), None],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        table_data = TableData(table_name, headers, rows)

        assert table_data.num_columns == 2
        assert table_data.num_rows == expected


class Test_TableData_eq:

    __DATA_0 = TableData(
        "Sheet1",
        ["i", "f", "c", "if", "ifc", "bool", "inf", "nan", "mix_num", "time"],
        [
            [1, "1.1", "aa", 1, 1, "True", float("inf"), "nan", 1, "2017-01-01T00:00:00"],
            [
                2,
                "2.2",
                "bbb",
                "2.2",
                "2.2",
                "False",
                float("inf"),
                float("NaN"),
                float("inf"),
                "2017-01-02 03:04:05+09:00",
            ],
            [
                3,
                "3.33",
                "cccc",
                -3,
                "ccc",
                "True",
                float("inf"),
                float("NaN"),
                float("NaN"),
                "2017-01-01T00:00:00",
            ],
        ],
    )
    __DATA_10 = TableData("tablename", ["a", "b"], [])
    __DATA_11 = TableData("tablename", ["a", "b"], [[1, 2], [11, 12]])

    @pytest.mark.parametrize(
        ["lhs", "rhs", "expected"],
        [[__DATA_0, __DATA_0, True], [__DATA_0, __DATA_10, False], [__DATA_10, __DATA_11, False]],
    )
    def test_normal(self, lhs, rhs, expected):
        assert (lhs == rhs) == expected
        assert (lhs != rhs) == (not expected)


class Test_TableData_equals:

    __LHS = TableData("tablename", ["a", "b"], [{"a": 1, "b": 2}, {"a": 11, "b": 12}])
    __RHS = TableData("tablename", ["a", "b"], [[1, 2], [11, 12]])

    @pytest.mark.parametrize(
        ["lhs", "rhs", "cmp_by_dp", "expected"],
        [[__LHS, __RHS, True, True], [__LHS, __RHS, False, False]],
    )
    def test_normal(self, lhs, rhs, cmp_by_dp, expected):
        empty_td = TableData("tablename", ["a", "b"], None)

        assert lhs.equals(rhs, cmp_by_dp=cmp_by_dp) == expected
        assert lhs.equals(empty_td, cmp_by_dp=cmp_by_dp) is False
        assert empty_td.equals(rhs, cmp_by_dp=cmp_by_dp) is False
        assert (lhs == rhs) is False
        assert (lhs != rhs) is True

        assert lhs.in_tabledata_list([rhs, empty_td], cmp_by_dp=cmp_by_dp) == expected
        assert lhs.in_tabledata_list([lhs, empty_td], cmp_by_dp=cmp_by_dp)
        assert lhs.in_tabledata_list([rhs, lhs, empty_td], cmp_by_dp=cmp_by_dp)
        assert empty_td.in_tabledata_list([rhs, lhs], cmp_by_dp=cmp_by_dp) is False


class Test_TableData_repr:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                "table_name=normal, headers=[a, b], cols=2, rows=2",
            ],
            [
                "null_header",
                None,
                [[1, 2], [3, 4]],
                "table_name=null_header, headers=[], cols=2, rows=2",
            ],
            [
                "null_header",
                [],
                [[1, 2], [3, 4]],
                "table_name=null_header, headers=[], cols=2, rows=2",
            ],
            ["null_body", ["a", "b"], [], "table_name=null_body, headers=[a, b], cols=2, rows=0"],
            ["マルチバイト", ["いろは", "漢字"], [], "table_name=マルチバイト, headers=[いろは, 漢字], cols=2, rows=0"],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert str(tabledata) == expected


class Test_TableData_as_dict:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "normal",
                ["a", "b"],
                [[1, 2], [3, 4]],
                {"normal": [OrderedDict([("a", 1), ("b", 2)]), OrderedDict([("a", 3), ("b", 4)])]},
            ],
            [
                None,
                ["a", "b"],
                [[1, 2], [3, 4]],
                {None: [OrderedDict([("a", 1), ("b", 2)]), OrderedDict([("a", 3), ("b", 4)])]},
            ],
            [
                "number",
                ["a", "b"],
                [[1, 2.0], [3.3, Decimal("4.4")]],
                {
                    "number": [
                        OrderedDict([("a", 1), ("b", 2)]),
                        OrderedDict([("a", Decimal("3.3")), ("b", Decimal("4.4"))]),
                    ]
                },
            ],
            [
                "include_none",
                ["a", "b"],
                [[None, 2], [None, None], [3, None], [None, None]],
                {"include_none": [OrderedDict([("b", 2)]), OrderedDict([("a", 3)])]},
            ],
            ["empty_records", ["a", "b"], [], {"empty_records": []}],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        assert TableData(table_name, headers, rows).as_dict() == expected


class Test_TableData_as_tuple:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            ["normal", ["a", "b"], [[1, 2], [3, 4]], [(1, 2), (3, 4)]],
            [None, ["a", "b"], [[1, 2], [3, 4]], [(1, 2), (3, 4)]],
            [
                "number",
                ["a", "b"],
                [[1, 2.0], [3.3, Decimal("4.4")]],
                [(1, 2.0), (Decimal("3.3"), Decimal("4.4"))],
            ],
            [
                "include_none",
                ["a", "b"],
                [[None, 2], [None, None], [3, None], [None, None]],
                [(None, 2), (None, None), (3, None), (None, None)],
            ],
            ["empty_records", ["a", "b"], [], []],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        for lhs, rhs in zip(TableData(table_name, headers, rows).as_tuple(), expected):
            print("lhs: {}".format(lhs), file=sys.stderr)
            print("rhs: {}".format(rhs), file=sys.stderr)

            assert tuple(lhs) == rhs


class Test_TableData_transpose:
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [
                TableData("tablename", ["a", "b"], [[1, 2, 3], [1, 2, 3]]),
                TableData("tablename", ["a", "b"], [[1, 1], [2, 2], [3, 3]]),
            ]
        ],
    )
    def test_normal(self, value, expected):
        assert value.transpose() == expected


class Test_TableData_value_dp_matrix:

    __MIXED_DATA = [
        [1, 2],
        (3, 4),
        {"attr_a": 5, "attr_b": 6},
        {"attr_a": 7, "attr_b": 8, "not_exist_attr": 100},
        {"attr_a": 9},
        {"attr_b": 10},
        {},
        NamedTuple2(11, None),
    ]

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "mixdata",
                attr_list_2,
                __MIXED_DATA,
                TableData(
                    "mixdata",
                    attr_list_2,
                    [
                        [1, 2],
                        [3, 4],
                        [5, 6],
                        [7, 8],
                        [9, None],
                        [None, 10],
                        [None, None],
                        [11, None],
                    ],
                ),
            ],
            [
                "none_header",
                None,
                [[1, 2], [3, 4]],
                TableData("none_header", None, [[1, 2], [3, 4]]),
            ],
            ["none_records", ["a", "b"], None, TableData("none_records", ["a", "b"], [])],
            ["none_data", None, None, TableData("none_data", [], [])],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert not tabledata.has_value_dp_matrix
        assert tabledata.value_dp_matrix == expected.value_dp_matrix
        assert tabledata.has_value_dp_matrix


class Test_TableData_is_empty_header:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [["tablename", [], [], True], ["tablename", ["a", "b"], [], False]],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert tabledata.is_empty_header() == expected


class Test_TableData_is_empty_rows:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            ["tablename", [], [], True],
            ["tablename", ["a", "b"], [], True],
            ["tablename", ["a", "b"], [[1, 2]], False],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert tabledata.is_empty_rows() == expected


class Test_TableData_is_empty:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            ["tablename", [], [], True],
            ["tablename", ["a", "b"], [], True],
            ["tablename", ["a", "b"], [[1, 2]], False],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        tabledata = TableData(table_name, headers, rows)

        assert tabledata.is_empty() == expected


class Test_TableData_validate_rows:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows"],
        [["tablename", [], []], ["tablename", ["a", "b"], []], ["tablename", ["a", "b"], [[1, 2]]]],
    )
    def test_normal(self, table_name, headers, rows):
        TableData(table_name, headers, rows).validate_rows()

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            ["tablename", ["a", "b"], [[1]], ValueError],
            ["tablename", ["a", "b"], [[1, 2, 3]], ValueError],
        ],
    )
    def test_exception(self, table_name, headers, rows, expected):
        with pytest.raises(expected):
            TableData(table_name, headers, rows).validate_rows()


class Test_TableData_filter_column:
    HEADERS = ["abcde", "test"]
    VALUE_MATRIX = [[1, 2], [3, 4]]

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "pattern", "is_invert_match", "expected"],
        [
            [
                "match",
                HEADERS,
                VALUE_MATRIX,
                ["abcde"],
                False,
                TableData("match", ["abcde"], [[1], [3]]),
            ],
            [
                "multiple_match",
                HEADERS,
                VALUE_MATRIX,
                ["abcde", "test"],
                False,
                TableData("multiple_match", ["abcde", "test"], [[1, 2], [3, 4]]),
            ],
            [
                "invert_match",
                HEADERS,
                VALUE_MATRIX,
                ["abcde"],
                True,
                TableData("invert_match", ["test"], [[2], [4]]),
            ],
            ["none", HEADERS, VALUE_MATRIX, None, False, TableData("none", HEADERS, VALUE_MATRIX)],
            ["empty", HEADERS, VALUE_MATRIX, [], False, TableData("empty", HEADERS, VALUE_MATRIX)],
        ],
    )
    def test_normal_match(self, table_name, headers, rows, pattern, is_invert_match, expected):
        tabledata = TableData(table_name, headers, rows)
        actual = tabledata.filter_column(patterns=pattern, is_invert_match=is_invert_match)

        dumps_results(expected=expected, actual=tabledata)

        assert actual == expected

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "pattern", "is_invert_match", "expected"],
        [
            [
                "multiple_patterns",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["test[0-9]+", "AAA_[a-z]+"],
                False,
                TableData(
                    "multiple_patterns",
                    ["test001_AAA", "AAA_test1234", "AAA_hoge"],
                    [[1, 2, 4], [11, 12, 14]],
                ),
            ],
            [
                "re_match_pattern",
                HEADERS,
                VALUE_MATRIX,
                ["abc*"],
                False,
                TableData("re_match_pattern", ["abcde"], [[1], [3]]),
            ],
            [
                "re_invert_match_pattern",
                HEADERS,
                VALUE_MATRIX,
                ["abc*"],
                True,
                TableData("re_invert_match_pattern", ["test"], [[2], [4]]),
            ],
            [
                "re_invert_unmatch_pattern",
                HEADERS,
                VALUE_MATRIX,
                ["unmatch_pattern"],
                True,
                TableData("re_invert_unmatch_pattern", HEADERS, VALUE_MATRIX),
            ],
        ],
    )
    def test_normal_re_match(self, table_name, headers, rows, pattern, is_invert_match, expected):
        tabledata = TableData(table_name, headers, rows)
        actual = tabledata.filter_column(
            patterns=pattern, is_invert_match=is_invert_match, is_re_match=True
        )

        dumps_results(expected=expected, actual=tabledata)

        assert actual == expected

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "pattern", "is_invert_match", "expected"],
        [
            [
                "match_and",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["[0-9]+", "AAA"],
                False,
                TableData("match_and", ["test001_AAA", "AAA_test1234"], [[1, 2], [11, 12]]),
            ],
            [
                "unmatch_and",
                ["test001_AAA", "AAA_test1234", "foo", "AAA_hoge"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                ["1234", "hoge"],
                True,
                TableData("unmatch_and", ["test001_AAA", "foo"], [[1, 3], [11, 13]]),
            ],
        ],
    )
    def test_normal_pattern_match(
        self, table_name, headers, rows, pattern, is_invert_match, expected
    ):
        tabledata = TableData(table_name, headers, rows)
        actual = tabledata.filter_column(
            patterns=pattern,
            is_invert_match=is_invert_match,
            is_re_match=True,
            pattern_match=PatternMatch.AND,
        )

        dumps_results(expected=expected, actual=tabledata)

        assert actual == expected

    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "pattern", "is_invert_match", "is_re_match", "expected"],
        [
            [
                "unmatch_pattern",
                HEADERS,
                VALUE_MATRIX,
                ["abc"],
                False,
                False,
                TableData("unmatch_pattern", [], []),
            ],
            [
                "none_pattern",
                HEADERS,
                VALUE_MATRIX,
                None,
                False,
                False,
                TableData("none_pattern", HEADERS, VALUE_MATRIX),
            ],
        ],
    )
    def test_normal_unmatch(
        self, table_name, headers, rows, pattern, is_invert_match, is_re_match, expected
    ):
        tabledata = TableData(table_name, headers, rows)
        actual = tabledata.filter_column(
            patterns=pattern, is_invert_match=is_invert_match, is_re_match=is_re_match
        )

        assert actual == expected

# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import re
from collections import OrderedDict
from decimal import Decimal

import dataproperty as dp
import six
import typepy
from six.moves import zip
from typepy import Nan

from ._constant import PatternMatch
from ._converter import to_value_matrix
from ._logger import logger
from .error import InvalidDataError


class TableData(object):
    """
    Class to represent a table data structure.

    :param str table_name: Name of the table.
    :param list header_list: Table header names.
    :param list record_list: Table data records.
    """

    @property
    def table_name(self):
        """
        :return: Name of the table.
        :rtype: str
        """

        return self.__table_name

    @table_name.setter
    def table_name(self, value):
        self.__table_name = value

    @property
    def header_list(self):
        """
        :return: Table header names.
        :rtype: list
        """

        return self.__dp_extractor.header_list

    @property
    def row_list(self):
        """
        :return: Table rows.
        :rtype: list
        """

        return self.__row_list

    @property
    def value_matrix(self):
        """
        :return: Table data rows.
        :rtype: list
        """

        if self.__value_matrix:
            return self.__value_matrix

        self.__value_matrix = [
            [value_dp.data for value_dp in value_dp_list]
            for value_dp_list in self.value_dp_matrix
        ]

        return self.__value_matrix

    @property
    def has_value_dp_matrix(self):
        return self.__value_dp_matrix is not None

    @property
    def num_rows(self):
        """
        :return:
            Number of rows in the tabular data.
            |None| if the ``row_list`` is neither list nor tuple.
        :rtype: int
        """

        try:
            return len(self.row_list)
        except TypeError:
            return None

    @property
    def num_columns(self):
        if typepy.is_not_empty_sequence(self.header_list):
            return len(self.header_list)

        try:
            return len(self.row_list[0])
        except TypeError:
            return None
        except IndexError:
            return 0

    @property
    def value_dp_matrix(self):
        """
        :return: DataProperty for table data.
        :rtype: list
        """

        if self.__value_dp_matrix is None:
            self.__value_dp_matrix = self.__dp_extractor.to_dp_matrix(
                to_value_matrix(self.header_list, self.row_list))

        return self.__value_dp_matrix

    @property
    def header_dp_list(self):
        return self.__dp_extractor.to_header_dp_list()

    @property
    def dp_extractor(self):
        return self.__dp_extractor

    def __init__(self, table_name, header_list, row_list, dp_extractor=None):
        self.__table_name = table_name
        self.__value_matrix = None
        self.__value_dp_matrix = None

        if row_list:
            self.__row_list = row_list
        else:
            self.__row_list = []

        if dp_extractor:
            self.__dp_extractor = dp_extractor
        else:
            self.__dp_extractor = dp.DataPropertyExtractor()

        self.__dp_extractor.strip_str_header = '"'

        if six.PY2:
            # avoid unit test execution hang up at Python 2 environment
            self.__dp_extractor.max_workers = 1

        if not header_list:
            self.__dp_extractor.header_list = []
        else:
            self.__dp_extractor.header_list = header_list

    def __repr__(self):
        element_list = [
            "table_name={}".format(self.table_name),
        ]

        try:
            element_list.append("header_list=[{}]".format(", ".join(self.header_list)))
        except TypeError:
            element_list.append("header_list=None")

        element_list.append("rows={}".format(self.num_rows))

        return ", ".join(element_list)

    def __eq__(self, other):
        return self.equals(other, is_strict=True)

    def __ne__(self, other):
        return not self.equals(other, is_strict=True)

    def is_empty_header(self):
        """
        :return: |True| if the data :py:attr:`.header_list` is empty.
        :rtype: bool
        """

        return typepy.is_empty_sequence(self.header_list)

    def is_empty_record(self):
        """Depricated"""

        return self.is_empty_rows()

    def is_empty_rows(self):
        """
        :return: |True| if the tabular data has no rows.
        :rtype: bool
        """

        return self.num_rows == 0

    def is_empty(self):
        """
        :return:
            |True| if the data :py:attr:`.header_list` or
            :py:attr:`.value_matrix` is empty.
        :rtype: bool
        """

        return any([self.is_empty_header(), self.is_empty_rows()])

    def equals(self, other, is_strict=False):
        if is_strict:
            return self.__equals_raw(other)

        return self.__equals_dp(other)

    def __equals_base(self, other):
        compare_item_list = [
            self.table_name == other.table_name,
        ]

        if self.num_rows is not None:
            compare_item_list.append(self.num_rows == other.num_rows)

        return all(compare_item_list)

    def __equals_raw(self, other):
        if not self.__equals_base(other):
            return False

        if self.header_list != other.header_list:
            return False

        for lhs_row, rhs_row in zip(self.row_list, other.row_list):
            if len(lhs_row) != len(rhs_row):
                return False

            if not all([
                lhs == rhs for lhs, rhs in zip(lhs_row, rhs_row)
                if not Nan(lhs).is_type() and not Nan(rhs).is_type()
            ]):
                return False

        return True

    def __equals_dp(self, other):
        if not self.__equals_base(other):
            return False

        if self.header_dp_list != other.header_dp_list:
            return False

        for lhs_list, rhs_list in zip(self.value_dp_matrix, other.value_dp_matrix):
            if len(lhs_list) != len(rhs_list):
                return False

            if any([lhs != rhs for lhs, rhs in zip(lhs_list, rhs_list)]):
                return False

        return True

    def in_tabledata_list(self, other, is_strict=False):
        for table_data in other:
            if self.equals(table_data, is_strict=is_strict):
                return True

        return False

    def validate_rows(self):
        """
        :raises ValueError:
        """

        invalid_row_idx_list = []

        for row_idx, row in enumerate(self.row_list):
            if isinstance(row, (list, tuple)) and len(self.header_list) != len(row):
                invalid_row_idx_list.append(row_idx)

            if isinstance(row, dict):
                if not all([header in row for header in self.header_list]):
                    invalid_row_idx_list.append(row_idx)

        if not invalid_row_idx_list:
            return

        raise ValueError(
            "header length and value length are mismatch:\n" +
            "  header({}): {}\n".format(len(self.header_list), self.header_list) +
            "  # of miss match rows: {} ouf of {}\n".format(
                len(invalid_row_idx_list), self.num_rows))

    def as_dict(self):
        """
        :return: Table data as a |dict| instance.
        :rtype: dict

        :Sample Code:
            .. code:: python

                from tabledata import TableData

                TableData(
                    table_name="sample",
                    header_list=["a", "b"],
                    row_list=[[1, 2], [3.3, 4.4]]
                ).as_dict()

        :Output:
            .. code:: json

                {'sample': [OrderedDict([('a', 1), ('b', 2)]),
                  OrderedDict([('a', 3.3), ('b', 4.4)])]}
        """

        from typepy import Typecode

        dict_body = []
        for value_dp_list in self.value_dp_matrix:
            if typepy.is_empty_sequence(value_dp_list):
                continue

            row = [
                (header, value_dp.data)
                for header, value_dp in zip(self.header_list, value_dp_list)
                if value_dp.typecode != Typecode.NONE
            ]

            if typepy.is_empty_sequence(row):
                continue

            dict_body.append(OrderedDict(row))

        return {self.table_name: dict_body}

    def as_dataframe(self):
        """
        :return: Table data as a ``pandas.DataFrame`` instance.
        :rtype: pandas.DataFrame

        :Sample Code:
            .. code-block:: python

                from tabledata import TableData

                TableData(
                    table_name="sample",
                    header_list=["a", "b"],
                    row_list=[[1, 2], [3.3, 4.4]]
                ).as_dict()

        :Output:
            .. code-block:: none

                     a    b
                0    1    2
                1  3.3  4.4

        :Dependency Packages:
            - `pandas <http://pandas.pydata.org/>`__
        """

        import pandas

        dataframe = pandas.DataFrame(self.value_matrix)
        if not self.is_empty_header():
            dataframe.columns = self.header_list

        return dataframe

    def filter_column(
            self, pattern_list=None, is_invert_match=False,
            is_re_match=False, pattern_match=PatternMatch.OR):
        logger.debug(
            "filter_column: pattern_list={}, is_invert_match={}, "
            "is_re_match={}, pattern_match={}".format(
                pattern_list, is_invert_match, is_re_match, pattern_match))

        if not pattern_list:
            return TableData(
                table_name=self.table_name, header_list=self.header_list, row_list=self.row_list)

        match_header_list = []
        match_column_matrix = []

        if pattern_match == PatternMatch.OR:
            match_method = any
        elif pattern_match == PatternMatch.AND:
            match_method = all
        else:
            raise ValueError("unknown matching: {}".format(pattern_match))

        for header, column in zip(self.header_list, zip(*self.row_list)):
            is_match_list = []
            for pattern in pattern_list:
                is_match = self.__is_match(header, pattern, is_re_match)

                is_match_list.append(any([
                    is_match and not is_invert_match,
                    not is_match and is_invert_match,
                ]))

            if match_method(is_match_list):
                match_header_list.append(header)
                match_column_matrix.append(column)

        logger.debug("filter_column: table={}, match_header_list={}".format(
            self.table_name, match_header_list))

        return TableData(
            table_name=self.table_name, header_list=match_header_list,
            row_list=list(zip(*match_column_matrix)))

    @staticmethod
    def from_dataframe(dataframe, table_name=""):
        """
        Initialize TableData instance from a pandas.DataFrame instance.

        :param pandas.DataFrame dataframe:
        :param str table_name: Table name to create.
        """

        return TableData(
            table_name=table_name,
            header_list=list(dataframe.columns.values),
            row_list=dataframe.values.tolist())

    @staticmethod
    def __is_match(header, pattern, is_re_match):
        if is_re_match:
            return re.search(pattern, header) is not None

        return header == pattern

    def __to_value_matrix(self, value_matrix):
        """
        Convert matrix to rows
        """

        self.__dp_extractor.float_type = Decimal

        if typepy.is_empty_sequence(self.header_list):
            return value_matrix

        if self.__dp_extractor.max_workers <= 1:
            return self.__to_value_matrix_st(value_matrix)

        return self.__to_value_matrix_mt(value_matrix)

    def __to_value_matrix_st(self, value_matrix):
        return [
            _to_row_helper(self.__dp_extractor, self.header_list, value_list, row_idx)[1]
            for row_idx, value_list in enumerate(value_matrix)
        ]

    def __to_value_matrix_mt(self, value_matrix):
        from concurrent import futures

        row_map = {}
        try:
            with futures.ProcessPoolExecutor(self.__dp_extractor.max_workers) as executor:
                future_list = [
                    executor.submit(
                        _to_row_helper, self.__dp_extractor,
                        self.header_list, value_list, row_idx)
                    for row_idx, value_list in enumerate(value_matrix)
                ]

                for future in futures.as_completed(future_list):
                    row_idx, row = future.result()
                    row_map[row_idx] = row
        finally:
            logger.debug("shutdown ProcessPoolExecutor")
            executor.shutdown()

        return [row_map[row_idx] for row_idx in sorted(row_map)]


def _to_row_helper(extractor, header_list, values, row_idx):
    """
    Convert values to a row.

    :param values: Value to be converted.
    :type values: |dict|/|namedtuple|/|list|/|tuple|
    :raises ValueError: If the ``values`` is invalid.
    """

    try:
        values = values._asdict()
    except AttributeError:
        pass

    if isinstance(values, dict):
        try:
            return (
                row_idx,
                [
                    dp.data
                    for dp in extractor.to_dp_list([
                        values.get(header) for header in header_list])
                ])
        except AttributeError:
            pass

    try:
        return (row_idx, [dp.data for dp in extractor.to_dp_list(values)])
    except TypeError:
        raise InvalidDataError("row must be a list or tuple: actual={}".format(values))

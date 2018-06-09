# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import multiprocessing
import re
from collections import OrderedDict
from decimal import Decimal

import dataproperty as dp
import six
import typepy
from six.moves import zip

from ._constant import PatternMatch
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
    def value_dp_matrix(self):
        """
        :return: DataProperty for table data.
        :rtype: list
        """

        if self.__value_dp_matrix is None:
            self.__value_dp_matrix = self.__dp_extractor.to_dp_matrix(
                self.__preprocess_value_matrix(self.row_list))

        return self.__value_dp_matrix

    @property
    def header_dp_list(self):
        return self.__dp_extractor.to_header_dp_list()

    def __init__(
            self, table_name, header_list, record_list, dp_extractor=None,
            quoting_flags=None):

        if dp_extractor:
            self.__dp_extractor = dp_extractor
        else:
            self.__dp_extractor = dp.DataPropertyExtractor()

        if quoting_flags:
            self.__dp_extractor.quoting_flags = quoting_flags
        self.__dp_extractor.strip_str_header = '"'

        if six.PY2:
            # avoid unit test execution hang up at Python 2 environment
            self.__dp_extractor.max_workers = 1

        self.__table_name = table_name
        self.__value_matrix = None
        self.__value_dp_matrix = None

        if not header_list:
            self.__dp_extractor.header_list = []
        else:
            self.__dp_extractor.header_list = header_list

        if not record_list:
            self.__row_list = []
        else:
            self.__row_list = record_list

    def __repr__(self):
        element_list = [
            "table_name={}".format(self.table_name),
        ]

        try:
            element_list.append("header_list=[{}]".format(", ".join(self.header_list)))
        except TypeError:
            element_list.append("header_list=None")

        element_list.append("rows={}".format(len(self.row_list)))

        return ", ".join(element_list)

    def __eq__(self, other):
        if not all([
            self.table_name == other.table_name,
            self.header_list == other.header_list,
            len(self.value_dp_matrix) == len(other.value_dp_matrix),
        ]):
            return False

        for lhs_list, rhs_list in zip(self.value_dp_matrix, other.value_dp_matrix):
            if len(lhs_list) != len(rhs_list):
                return False

            if not all([lhs == rhs for lhs, rhs in zip(lhs_list, rhs_list)]):
                return False

        return True

    def __ne__(self, other):
        if any([
            self.table_name != other.table_name,
            self.header_list != other.header_list,
            len(self.value_dp_matrix) != len(other.value_dp_matrix),
        ]):
            return True

        for lhs_list, rhs_list in zip(self.value_dp_matrix, other.value_dp_matrix):
            if len(lhs_list) != len(rhs_list):
                return True

            if any([lhs != rhs for lhs, rhs in zip(lhs_list, rhs_list)]):
                return True

        return False

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

        try:
            return not typepy.is_not_empty_sequence(self.row_list[0])
        except (TypeError, IndexError):
            return True

    def is_empty(self):
        """
        :return:
            |True| if the data :py:attr:`.header_list` or
            :py:attr:`.value_matrix` is empty.
        :rtype: bool
        """

        return any([self.is_empty_header(), self.is_empty_rows()])

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
                    record_list=[[1, 2], [3.3, 4.4]]
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
                    record_list=[[1, 2], [3.3, 4.4]]
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
                table_name=self.table_name, header_list=self.header_list,
                record_list=self.row_list)

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
            record_list=list(zip(*match_column_matrix)))

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
            record_list=dataframe.values.tolist())

    @staticmethod
    def __is_match(header, pattern, is_re_match):
        if is_re_match:
            return re.search(pattern, header) is not None

        return header == pattern

    def __preprocess_value_matrix(self, value_matrix):
        return [
            _preprocess_value_list(self.header_list, value_list, row_idx)[1]
            for row_idx, value_list in enumerate(value_matrix)
        ]

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


def _preprocess_value_list(header_list, values, row_idx):
    if header_list:
        try:
            values = values._asdict()
        except AttributeError:
            pass

        try:
            return (row_idx, [values.get(header) for header in header_list])
        except (TypeError, AttributeError):
            pass

    if not isinstance(values, (tuple, list)):
        raise InvalidDataError("row must be a list or tuple: actual={}".format(values))

    return (row_idx, values)


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

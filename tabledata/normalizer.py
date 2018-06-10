# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import abc

import pathvalidate as pv
import six
import typepy

from ._core import TableData
from .error import InvalidHeaderNameError, InvalidTableNameError


@six.add_metaclass(abc.ABCMeta)
class TableDataNormalizerInterface(object):
    """
    Interface class to validate and normalize data of |TableData|.
    """

    @abc.abstractmethod
    def validate(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def normalize(self):  # pragma: no cover
        pass


class AbstractTableDataNormalizer(TableDataNormalizerInterface):

    def __init__(self, tabledata):
        self._tabledata = tabledata

    def validate(self):
        self._validate_table_name(self._tabledata.table_name)
        self._validate_header_list()

    def sanitize(self):
        """Deprecated"""

        return self.normalize()

    def normalize(self):
        """
        :return: Sanitized table data.
        :rtype: tabledata.TableData
        """

        return TableData(
            self.__normalize_table_name(),
            self._normalize_header_list(),
            self._normalize_row_list(),
            dp_extractor=self._tabledata.dp_extractor)

    @abc.abstractmethod
    def _preprocess_table_name(self):
        """
        Always called before table name validation.
        You must return preprocessed table name.
        """

    @abc.abstractmethod
    def _validate_table_name(self, table_name):
        """
        Must raise :py:class:`~.InvalidTableNameError`
        when you consider the table name invalid.

        :param str header: Table name to validate.
        :raises pytablereader.InvalidTableNameError:
            If the table name is invalid.
            |raises_validate_table_name|
        """

    @abc.abstractmethod
    def _normalize_table_name(self, table_name):
        """
        Must return a valid table name.
        The table name must be a valid name with
        :py:meth:`~._validate_table_name` method.

        This method called when :py:meth:`~._validate_table_name` method raise
        :py:class:`~.InvalidTableNameError`.

        :param str table_name: Table name to normalize.
        :return: Sanitized table name.
        :rtype: str
        """

    @abc.abstractmethod
    def _preprocess_header(self, col_idx, header):
        """
        Always called before a header validation.
        You must return preprocessed header.
        """

    @abc.abstractmethod
    def _validate_header(self, header):
        """
        No operation.

        This method called for each table header. Override this method
        in subclass if you want to detect invalid table header element.
        Raise :py:class:`~.InvalidHeaderNameError` if an invalid
        header element found.

        :param str header: Table header name.
        :raises pytablereader.InvalidHeaderNameError:
            If the ``header`` is invalid.
        """

    @abc.abstractmethod
    def _normalize_header(self, header):
        """
        Must return a valid header name.
        This method called when :py:meth:`~._validate_header` method raise
        :py:class:`~.InvalidHeaderNameError`.
        Override this method in subclass if you want to rename invalid
        table header element.

        :param str header: Header name to normalize.
        :return: Renamed header name.
        :rtype: str
        """

    def _normalize_row_list(self):
        return self._tabledata.row_list

    def _validate_header_list(self):
        for header in self._tabledata.header_list:
            self._validate_header(header)

    def __normalize_table_name(self):
        preprocessed_table_name = self._preprocess_table_name()

        try:
            self._validate_table_name(preprocessed_table_name)
            new_table_name = preprocessed_table_name
        except InvalidTableNameError:
            new_table_name = self._normalize_table_name(preprocessed_table_name)
            self._validate_table_name(new_table_name)
        except pv.NullNameError as e:
            raise InvalidTableNameError(e)

        return new_table_name

    def _normalize_header_list(self):
        new_header_list = []

        for col_idx, header in enumerate(self._tabledata.header_list):
            header = self._preprocess_header(col_idx, header)

            try:
                self._validate_header(header)
                new_header = header
            except InvalidHeaderNameError:
                new_header = self._normalize_header(header)
                self._validate_header(new_header)
            except pv.NullNameError as e:
                raise InvalidHeaderNameError(e)

            new_header_list.append(new_header)

        return new_header_list


class TableDataNormalizer(AbstractTableDataNormalizer):

    def _preprocess_table_name(self):
        return self._tabledata.table_name

    def _validate_table_name(self, table_name):
        try:
            typepy.String(table_name).validate()
        except TypeError as e:
            raise InvalidTableNameError(e)

    def _normalize_table_name(self, table_name):
        return typepy.String(table_name).force_convert()

    def _preprocess_header(self, col_idx, header):
        return header

    def _validate_header(self, header):
        try:
            typepy.String(header).validate()
        except TypeError as e:
            raise InvalidHeaderNameError(e)

    def _normalize_header(self, header):
        return typepy.String(header).force_convert()

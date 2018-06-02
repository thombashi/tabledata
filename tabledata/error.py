# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import


class NameValidationError(ValueError):
    """
    Base name error class.
    """


class InvalidTableNameError(NameValidationError):
    """
    Exception raised when the table name is invalid.
    """


class InvalidHeaderNameError(NameValidationError):
    """
    Exception raised when a table header name is invalid.
    """


class DataError(ValueError):
    """
    Exception raised when data is invalid as tabular data.
    """


class InvalidDataError(DataError):
    """
    Deprecate:
    Exception raised when data is invalid as tabular data.
    """


class EmptyDataError(InvalidDataError):
    """
    Deprecate:
    Exception raised when data does not include valid table data.
    """

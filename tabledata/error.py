# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import


class NameError(ValueError):
    """
    Base name error class.
    """


class InvalidTableNameError(NameError):
    """
    Exception raised when the table name is invalid.
    """


class InvalidHeaderNameError(NameError):
    """
    Exception raised when a table header name is invalid.
    """


class InvalidDataError(ValueError):
    """
    Exception raised when data is invalid as tabular data.
    """


class EmptyDataError(InvalidDataError):
    """
    Exception raised when data does not include valid table data.
    """

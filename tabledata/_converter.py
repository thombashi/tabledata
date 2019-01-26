# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from .error import DataError


def to_value_matrix(headers, value_matrix):
    if value_matrix is None:
        return []

    return [_to_row(headers, values, row_idx)[1] for row_idx, values in enumerate(value_matrix)]


def _to_row(headers, values, row_idx):
    if headers:
        try:
            values = values._asdict()
        except AttributeError:
            pass

        try:
            return (row_idx, [values.get(header) for header in headers])
        except (TypeError, AttributeError):
            pass

    if not isinstance(values, (tuple, list)):
        raise DataError("row must be a list or tuple: actual={}".format(type(values)))

    return (row_idx, values)

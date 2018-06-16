# encoding: utf-8

'''
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
'''

from __future__ import absolute_import, unicode_literals

from .error import InvalidDataError


def to_value_matrix(header_list, value_matrix):
    if value_matrix is None:
        return []

    return [
        _to_row(header_list, value_list, row_idx)[1]
        for row_idx, value_list in enumerate(value_matrix)
    ]


def _to_row(header_list, values, row_idx):
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

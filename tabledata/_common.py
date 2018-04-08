# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


def convert_idx_to_alphabet(column_idx):
    if column_idx < 26:
        return chr(65 + column_idx)

    div, mod = divmod(column_idx, 26)

    return (
        convert_idx_to_alphabet(div - 1) + convert_idx_to_alphabet(mod))

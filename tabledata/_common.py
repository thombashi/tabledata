# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import six


def convert_idx_to_alphabet(idx):
    if idx < 26:
        return six.unichr(65 + idx)

    div, mod = divmod(idx, 26)

    return convert_idx_to_alphabet(div - 1) + convert_idx_to_alphabet(mod)

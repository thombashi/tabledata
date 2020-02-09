# encoding: utf-8

from __future__ import print_function, unicode_literals

import pytest

from tabledata import set_logger


class Test_set_logger(object):
    @pytest.mark.parametrize(["value"], [[True], [False]])
    def test_smoke(self, value):
        set_logger(value)

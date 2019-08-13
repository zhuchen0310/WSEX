#! /usr/bin/python
# -*- coding:utf-8 -*-
# @zhuchen    : 2019-08-06 10:40

from .biki import biki
from .binance import binance
from .huobipro import huobipro

exchanges = [
    'biki',
    'binance',

]

__all__ = exchanges
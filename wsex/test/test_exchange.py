#! /usr/bin/python
# -*- coding:utf-8 -*-
# @zhuchen    : 2019-08-06 10:32
import asyncio

from colorama import Fore
from django.test import TestCase
from django.conf import settings

# TODO 导入 新接入的交易所
from wsex.biki import biki as Exchange
from wsex._base import WsTypeEnum

loop = asyncio.get_event_loop()
proxy = settings.PROXY


class ExchangeTests(TestCase):
    """
    说明:
        1. 在单个交易所中编辑 相应方法
        2. 导入交易所
        3. 执行测试命令: python manage.py test wsex.test.test_exchange -k
    """

    @classmethod
    def setUpTestData(cls):
        # TODO 设置ws 订阅类型
        ws_type = WsTypeEnum.kline.value
        cls.ws = Exchange(proxy=proxy, ws_type=ws_type)
        cls.symbol = list(cls.ws.symbols.keys())[0]

    def test_symbols(self):
        print(f'{Fore.LIGHTCYAN_EX}Start test symbol')
        self.assertIsInstance(self.ws.symbols, dict)
        one_value = list(self.ws.symbols.values())[0]
        self.assertTrue('/' in one_value or '_' in one_value)

    def test_restful_kline(self):
        print(f'{Fore.RED}Start test RESTful Kline...')
        ret = loop.run_until_complete(self.ws.get_restful_klines(self.symbol))
        print('*' * 20)
        print(ret)
        print('*' * 20)
        print()
        # [t, o, h, l, c, v]
        self.assertIsInstance(ret, list)
        self.assertEqual(len([x for x in ret if x]), 6)
        self.assertEqual(max([float(x) for x in ret[1:-1]]), float(ret[2]))
        self.assertEqual(min([float(x) for x in ret[1:-1]]), float(ret[3]))

    def test_restful_trade(self):
        print(f'{Fore.BLUE}Start test RESTful Trade...')
        ret = loop.run_until_complete(self.ws.get_restful_trades(self.symbol))
        print('*' * 20)
        print(ret)
        print('*' * 20)
        print()
        # [t, trade_id, b or s, price, amount]
        self.assertIsInstance(ret, list)
        self.assertEqual(len(ret), 5)
        self.assertIsInstance(ret[0], int)
        self.assertIn(ret[2], ['b', 's'])

    def test_websocket(self):
        print(f'{Fore.LIGHTGREEN_EX}Start test websocket...')
        self.ws.ping_interval_seconds = 5
        loop.run_until_complete(self.ws_go())

    async def ws_go(self):
        if self.ws.ws_type == WsTypeEnum.kline.value:
            sub_data = await self.ws.get_kline_sub_data(self.symbol)
        elif self.ws.ws_type == WsTypeEnum.trade.value:
            sub_data = await self.ws.get_trade_sub_data(self.symbol)
        ws_url = await self.ws.get_ws_url()
        await self.ws.add_sub_data(sub_data)
        self.assertNotEqual(len(self.ws._pending_sub_data), 0)
        await self.ws.get_ws_data_forever(ws_url)



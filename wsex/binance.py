#! /usr/bin/python
# -*- coding:utf-8 -*-
# @zhuchen    : 2019-03-04 16:36

from __future__ import absolute_import

import json

from ._base import ExchangeBase, WsTypeEnum
WS_TYPE_TRADE = WsTypeEnum.trade.value
WS_TYPE_KLINE = WsTypeEnum.kline.value


class binance(ExchangeBase):

    def __init__(self, loop=None, proxy=None, timeout=5, ws_type=WsTypeEnum.kline.value):
        super().__init__(loop, proxy, timeout, ws_type=ws_type)
        self.exchange_id = 'binance'
        self.http_timeout = 5
        self.ws_timeout = 5
        self.http_data = {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
            },
            'api': 'https://api.binance.com/api/v1',
            'urls': {
                'symbols': '/exchangeInfo',
                'trades': '/trades',
                'klines': '/klines'
            },
            'limits': {
                'kline': 200,
                'trade': 200,
            }
        }
        self.ws_data = {
            'api': {
                'ws_url': 'wss://stream.binance.com:9443/ws/'
            }
        }
        self.symbols = self.get_symbols()
        self.max_sub_num = 20  # 每个连接 最大订阅数
        self.is_send_sub_data = False

    def get_symbols(self):
        api = self.http_data['api']
        path = self.http_data['urls']['symbols']
        url = f'{api}{path}'
        data = self.http.requests_data(url)
        if not data or not data['symbols']:
            raise BaseException(f'{self.exchange_id} get symbols error')
        symbols = {
            x['symbol'].lower():
                f'{x["baseAsset"]}/{x["quoteAsset"]}'.upper()

            for x in data['symbols'] if x['status'] not in ['BREAK', 'break']
        }
        return symbols

    async def get_ws_url(self, ws_type=WS_TYPE_TRADE, symbols=None):
        """
        功能:
            生成 ws 链接
        """
        pair_url = ''
        if not symbols:
            symbols = list(self.symbols.keys())[:self.max_sub_num]
        if symbols:
            if ws_type == WS_TYPE_TRADE:
                pair_url = '/'.join([f"{symbol}@aggTrade" for symbol in symbols])
            elif ws_type == WS_TYPE_KLINE:
                pair_url = '/'.join([f"{symbol}@kline_1m" for symbol in symbols])
        url = f"{self.ws_data['api']['ws_url']}{pair_url}"
        return url

    async def get_restful_trade_url(self, symbol):
        """
        功能:
            获取 restful 请求的url
        """
        symbol = symbol.upper()
        api = self.http_data['api']
        path = self.http_data['urls']['trades']
        url = f'{api}{path}?symbol={symbol}&limit={self.http_data["limits"]["trade"]}'
        return url

    async def get_restful_kline_url(self, symbol, timeframe=None, limit=None):
        """
        功能:
            获取 restful 请求的url
        """
        api = self.http_data['api']
        path = self.http_data['urls']['klines']
        if limit:
            url = f'{api}{path}?symbol={symbol.upper()}&interval=1m&limit={limit}'
        else:
            url = f'{api}{path}?symbol={symbol.upper()}&interval=1m'
        return url

    async def parse_restful_trade(self, trades_data_list, symbol):
        """
        功能:
            处理 restful 返回 trade
            封装成统一格式 保存到Redis中
        返回:
            [[1551760709,"10047738192326012742563","ask",3721.94,0.0235]]
        """
        trade_list = []
        if not trades_data_list:
            return trade_list
        for x in trades_data_list:
            format_trade = await self.format_trade([
                int(x["time"]) // 1000,  # 秒级时间戳
                x["id"],
                'buy' if x['isBuyerMaker'] else 'sell',
                x["price"],
                x["qty"]
            ])
            if not format_trade:
                continue
            trade_list.append(format_trade)
        await self.save_trades_to_redis(symbol, trade_list)
        return trade_list

    async def parse_trade(self, msg, ws):
        """
        功能:
            处理 ws 实时trade
        """
        try:
            data = json.loads(msg)
        except:
            data = None
        if not data:
            return
        symbol = data['s'].lower()
        format_trade = await self.format_trade([
            int(data['T']) // 1000,
            data["a"],
            'buy' if data['m'] else 'sell',
            data['p'],
            data['q']

        ])
        if not format_trade:
            trade_list = []
        else:
            trade_list = [format_trade]
        await self.save_trades_to_redis(symbol, trade_list, ws)
        return

    async def parse_kline(self, msg, ws=None):
        try:
            data = json.loads(msg)
        except:
            data = None
        if not data:
            return
        kline = data['k']
        symbol = kline['s'].lower()
        if not symbol:
            return
        timestamp = int(kline['t']) // 1000
        ohlcv = await self.format_kline([
            timestamp,
            kline['o'],
            kline['h'],
            kline['l'],
            kline['c'],
            kline['v'],
        ])
        await self.save_kline_to_redis(symbol, ohlcv)

    async def parse_restful_kline(self, data):
        """
        功能:
            处理 restful 返回 kline
            统一格式 ohlcv = [tms, open, high, low, close, volume]
        """
        ohlcv_list = []
        if not data:
            return ohlcv_list
        for x in data:
            fmt_k = await self.format_kline([
                x[0] // 1000,
                x[1],
                x[2],
                x[3],
                x[4],
                x[5],
            ])
            if fmt_k:
                ohlcv_list.append(fmt_k)
        return ohlcv_list



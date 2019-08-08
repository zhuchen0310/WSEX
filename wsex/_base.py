#! /usr/bin/python
# -*- coding:utf-8 -*-
# @zhuchen    : 2019-08-06 10:35

import datetime
from enum import Enum

from wsex.utils.http_base import WSBase, HttpBase
from wsex.utils.logger_con import get_logger

logger = get_logger(__name__)


class WsTypeEnum(Enum):
    kline = 'kline'
    trade = 'trade'


class ExchangeBase(WSBase):

    def __init__(self, loop=None, proxy=None, timeout=5, ws_type=WsTypeEnum.kline.value):
        super().__init__(loop, proxy, timeout)
        self.http_proxy = proxy
        self.ws_proxy = proxy
        self.exchange_id = ''
        self.ws_type = ws_type
        self.http_timeout = timeout
        self.http_data = {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
                'Content-Type': "application/json",
            },
            'api': 'https://openapi.biki.com/open/api',
            'urls': {
                'symbols': '/common/symbols',
                'trades': '/get_trades?symbol={}',
                'klines': '/get_records?symbol={}&period=1'
            },
            'limits': {
                'kline': 200,
                'trade': 200,
            }
        }
        self.ws_data = {
            'api': {
                'ws_url': 'wss://ws.biki.com/kline-api/ws'
            }
        }
        self.http = HttpBase(loop=loop, proxy=proxy, timeout=timeout)
        self.is_send_sub_data = True

    async def str_2_timestamp(self, time_str: str, is_timedelta: bool = True, timedelta_hours: int = 8):
        """
        功能:
            时间str > 时间戳 秒级时间戳
        """
        format = '%Y-%m-%d %H:%M:%S'
        if 'T' in time_str:
            format = '%Y-%m-%dT%H:%M:%S'
        if '.' in time_str:
            format = f'{format}.%f'
        if 'Z' in time_str:
            format = f'{format}Z'
        if is_timedelta:
            tms = int((datetime.datetime.strptime(
                time_str, format) + datetime.timedelta(hours=timedelta_hours)).timestamp())
        else:
            tms = int((datetime.datetime.strptime(
                time_str, format)).timestamp())
        return tms

    def get_symbols(self):
        """
        功能:
            初始化 交易所 的 所有交易对
        """
        return {}

    async def get_restful_trade_url(self, symbol: str):
        """
        功能:
            获取 restful 请求的url
        """
        pass

    async def get_restful_kline_url(self, symbol: str, timeframe: str = None, limit: int = 0):
        """
        功能:
            获取 restful 请求的url 不需要 再正反序判断
        """
        pass

    async def parse_restful_trade(self, data: dict, symbol: str):
        """
        功能:
            处理 restful 返回 trade
            封装成统一格式 保存到Redis中
        返回:
            [[1551760709,"10047738192326012742563","buy",3721.94,0.0235]]
        """
        pass

    async def parse_restful_kline(self, data: dict):
        """
        功能:
            处理 restful 返回 kline
            统一格式 ohlcv = [tms, open, high, low, close, volume]
            tms 是 秒级
            注意时间戳 顺序: 从远到近
        """
        pass

    async def get_restful_trades(self, symbol: str):
        """
        功能:
            获取 RESTFUL trade
            is_save 只查还是要保存
            is_first_request 是否首次连接请求, 个别交易所订阅ws 后可以返回快照, 减少一次请求
        """
        url = await self.get_restful_trade_url(symbol)
        data = await self.http.get_json_data(url)
        return await self.parse_restful_trade(data, symbol)

    async def get_restful_klines(self, symbol: str, timeframe: str = None, limit: int = None):
        """
        功能:
            获取 RESTFUL klines
        """
        url = await self.get_restful_kline_url(symbol, timeframe, limit)
        data = await self.http.get_json_data(url)
        ret = await self.parse_restful_kline(data)
        if ret and ret[0][0] > ret[-1][0]:
            ret = ret[::-1]
        return ret

    async def parse_trade(self, msg: str, ws):
        """
        功能:
            处理 ws 实时trade
        """
        pass

    async def parse_kline(self, msg: str, ws):
        """
        功能:
            处理 ws 实时kline
        """
        pass

    async def on_message(self, ws, message: str):
        """
        功能:
            ws 消息处理函数
        """
        if self.ws_type == WsTypeEnum.kline.value:
            await self.parse_kline(message, ws)
        elif self.ws_type == WsTypeEnum.trade.value:
            await self.parse_trade(message, ws)

    async def format_trade(self, trade: list) -> list:
        """
        功能:
            格式化 trade 为统一格式
            [
                1111 ,      ----> timestamp int 秒
                '1211' ,    ----> trade_id str
                's' ,       ----> type str
                3400.3 ,    ----> price float
                0.3 ,       ----> amount float
            ]
        """
        try:
            ret_trade = [
                int(float(trade[0])) if not isinstance(trade[0], int) else trade[0],
                f'{trade[1]}',
                'b' if f'{trade[2]}' in ['buy', 'bid', 'b', 'BUY', 'BID', 'Buy', 'Bid'] else 's',
                float(trade[3]),
                float(trade[4]),
            ]
            return ret_trade
        except Exception as e:
            await logger.error(f'{self.exchange_id} format trade error: {e}')
            return []

    async def format_kline(self, kline: list) -> list:
        """
        功能:
            格式化 trade 为统一格式
            [
                1111 ,      ----> timestamp int 秒
                1 ,         ----> open float
                2 ,         ----> high float
                3 ,         ----> low float
                4 ,         ----> close float
                5 ,         ----> volume float
            ]
        """
        try:
            ret_kline = [
                int(float(kline[0])) if not isinstance(kline[0], int) else kline[0],
                float(kline[1]),
                float(kline[2]),
                float(kline[3]),
                float(kline[4]),
                float(kline[5]),
            ]
            return ret_kline
        except Exception as e:
            await logger.error(f'{self.exchange_id} format kline error: {e}, {kline}')
            return []

    async def save_trades_to_redis(self, symbol: str, trade_list: list, ws=None):
        """
        功能:
            保存 trades
        :param symbol:
        :param trade_list:
        :param ws:
        :return:
        """
        if trade_list:
            print(trade_list[0])
        pass

    async def save_kline_to_redis(self, symbol: str, kline: list, ws=None):
        """
        功能:
            保存 klines
        :param symbol:
        :param kline:
        :param ws:
        :return:
        """
        print(kline)
        pass

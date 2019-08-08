
WSEX – CryptoCurrency EXchange ws Trading Library
==============================================

pip 安装
~~~~~~
- 安装应用

.. code:: shell

    python setup.py install # 该命令会将当前的Python应用安装到当前Python环境的”site-packages”目录下，这样其他程序就可以像导入标准库一样导入该应用的代码了。

- 开发方式安装

.. code:: shell

    python setup.py develop # 如果应用在开发过程中会频繁变更，每次安装还需要先将原来的版本卸掉，很麻烦。使用”develop”开发方式安装的话，应用代码不会真的被拷贝到本地Python环境的”site-packages”目录下，而是在”site-packages”目录里创建一个指向当前应用位置的链接。这样如果当前位置的源码被改动，就会马上反映到”site-packages”里。


Docker
~~~~~~

.. code:: shell

    ./docker.sh drun

新交易所接入
~~~~~~

在wsex 中进行交易所接入

交易所接入参考示例:
    - biki 发送订阅
    - binance 在连接中订阅

主要实现方法:
    - def get_symbols(self) # 交易所支持交易对
    - async def parse_restful_trade(self)
    - async def parse_restful_kline(self)
    - async def parse_trade(self, msg, ws)
    - async def parse_kline(self, msg, ws)

在test_exchange 中导入新接入的交易所:

.. code:: shell

    from wsex import biki as Exchange

执行测试命令:

.. code:: shell

    python manage.py test wsex.test.test_exchange -k


iPython 7.0 中测试
~~~~~~

.. code:: shell

    import wsex
    symbol = 'btcusdt'
    ex = wsex.biki()
    # 获取klines
    await ex.get_restful_klines(symbol, '1min')
    # 获取trades
    await ex.get_restful_trades(symbol)

    # 普通的一次连接 发送订阅模式 biki:
    # is_send_sub_data = True
    ws_url = await ex.get_ws_url()
    # ws 获取kline 数据
    sub_data = await ex.get_kline_sub_data(symbol)
    # ws 获取trade 数据
    sub_data = await ex.get_trade_sub_data(symbol)
    await ex.add_sub_data(sub_data)
    await ex.get_ws_data_forever(ws_url)

    # 在连接中订阅模式 binance:
    # is_send_sub_data = False
    ex = wsex.binance()
    symbols = ['btcusdt']
    ws_type = 'kline'
    ws_url = await ex.get_ws_url(ws_type, symbols)
    await ex.get_ws_data_forever(ws_url)

ToDo
~~~~~~

- 支持 ticker
- 支持各周期 kline
- 同步模式

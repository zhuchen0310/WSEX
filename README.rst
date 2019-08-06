
## 使用说明：

- 作为包使用
    - 安装应用
    
        python setup.py install
    
        该命令会将当前的Python应用安装到当前Python环境的”site-packages”目录下，这样其他程序就可以像导入标准库一样导入该应用的代码了。

    - 开发方式安装
    
        python setup.py develop
    
        如果应用在开发过程中会频繁变更，每次安装还需要先将原来的版本卸掉，很麻烦。使用”develop”开发方式安装的话，应用代码不会真的被拷贝到本地Python环境的”site-packages”目录下，而是在”site-packages”目录里创建一个指向当前应用位置的链接。这样如果当前位置的源码被改动，就会马上反映到”site-packages”里。


- docker构建环境
    ```
    ~ ./docker.sh drun
    ```
- 在spider 中进行交易所接入
- 交易所接入参考示例: biki
- 主要实现方法: 
    - def get_symbols(self) # 交易所支持交易对
    - async def parse_restful_trade(self)
    - async def parse_restful_kline(self)
    - async def parse_trade(self, msg, ws)
    - async def parse_kline(self, msg, ws)
- 在test_exchange 中导入新接入的交易所
    ```
    from .biki import biki as Exchange
    ```
- 执行测试命令: 
    ```
    python manage.py test spider.test.test_exchange -k 
    ```
- 主要数据结构
    - trade
        ```
        [
            
            1562317469, # 时间: int 秒级时间戳
            'trade_id', # 订单id: str 
            'b',        # 交易类型: str 'b' or 's'
            11000.11,   # 价格: float
            0.001       # 成交量: float
        ]
        ```
    - kline
        ```
        [
            1573692000, # 时间: int 秒级 分钟时间戳
            11000.11,   # o开: float 
            11000.11,   # h高: float 
            11000.11,   # l低: float 
            11000.11,   # c关: float 
            0.11,       # v交易量: float 
        ]
        ```
      
- iPython 7.0 中测试
```python

import wsex

symbol = 'btcusdt'

ex = wsex.biki()

# 获取klines
await ex.get_restful_klines(symbol, '1min')

# 获取trades
await ex.get_restful_trades(symbol)

ws_url = await ex.get_ws_url()

# ws 获取kline 数据
sub_data = await ex.get_kline_sub_data(symbol)
# ws 获取trade 数据
sub_data = await ex.get_trade_sub_data(symbol)

await ex.add_sub_data(sub_data)
await ex.get_ws_data_forever(ws_url)
```
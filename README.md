### TEXS

- ##### 介绍

    TEXS: Token, Exchange, Spider 
    
- ##### 用途

    抓取交易所 WS, RESTful : Klines, Tickers, Trades. 实时计算各TimeFrameKline, 全网均价 
    
- ##### 架构

    使用Python 3.6 + Asyncio + LevelDB + Redis + Websocket + Prometheus + MQ + Postgres 
    
- ##### 功能

    支持分布式抓取, prometheus监控, 本地WebSocket 消息订阅, 中央调度, 异常切源, 数据自动校验补齐, FTP回传数据, k线实时计算, 全网均价计算....



静待开放...

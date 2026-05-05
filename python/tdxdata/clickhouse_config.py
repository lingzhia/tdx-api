# -*- coding: utf-8 -*-
"""
ClickHouse配置
"""

# ClickHouse连接配置
CH_HOST = "100.107.142.74"
CH_PORT = 9000
CH_USER = "Ling"
CH_PASSWORD = "@Lingzhi1996"
CH_DATABASE = "LingQuant"

# 表配置
CH_TABLE_KLINE_1MIN = "kline_1min"

# 同步配置
BATCH_SIZE = 1000  # 每批插入条数
REQUEST_TIMEOUT = 60  # 请求超时(秒)

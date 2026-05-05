# -*- coding: utf-8 -*-
"""
tdxdata 数据模型
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Quote:
    """五档行情"""
    code: str
    exchange: str
    last: float       # 昨收价(元)
    open: float       # 开盘价(元)
    high: float       # 最高价(元)
    low: float        # 最低价(元)
    close: float      # 最新价(元)
    volume: int       # 成交量(手)
    amount: float     # 成交额(元)
    inside_dish: int  # 内盘
    outer_disc: int   # 外盘
    buy1: float = 0
    buy1_vol: int = 0
    buy2: float = 0
    buy2_vol: int = 0
    buy3: float = 0
    buy3_vol: int = 0
    buy4: float = 0
    buy4_vol: int = 0
    buy5: float = 0
    buy5_vol: int = 0
    sell1: float = 0
    sell1_vol: int = 0
    sell2: float = 0
    sell2_vol: int = 0
    sell3: float = 0
    sell3_vol: int = 0
    sell4: float = 0
    sell4_vol: int = 0
    sell5: float = 0
    sell5_vol: int = 0


@dataclass
class Kline:
    """K线数据"""
    time: datetime
    open: float       # 开盘价(元)
    high: float       # 最高价(元)
    low: float        # 最低价(元)
    close: float      # 收盘价(元)
    volume: int       # 成交量(手)
    amount: float     # 成交额(元)


@dataclass
class Minute:
    """分时数据"""
    time: str         # HH:MM格式
    price: float      # 价格(元)
    volume: int       # 成交量(手)


@dataclass
class Trade:
    """逐笔成交"""
    time: datetime
    price: float      # 成交价(元)
    volume: int       # 成交量(手)
    status: int       # 0=买入,1=卖出,2=中性
    number: int       # 成交单数


@dataclass
class ETF:
    """ETF基金"""
    code: str
    name: str
    exchange: str
    last_price: float


@dataclass
class Task:
    """后台任务"""
    id: str
    type: str         # pull_kline, pull_trade
    status: str       # running, success, failed, cancelled
    started_at: str
    finished_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class WorkdayInfo:
    """交易日信息"""
    date: str
    numeric: str
    is_workday: bool
    next: List[dict]
    previous: List[dict]

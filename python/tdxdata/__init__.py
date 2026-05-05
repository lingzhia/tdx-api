# -*- coding: utf-8 -*-
"""
tdxdata - 通达信股票数据Python包

类jqdata风格的函数式接口，封装tdx-api全部32个RESTful接口。

使用示例:
    import tdxdata as tdx

    # 初始化
    tdx.auth()

    # 获取行情
    df = tdx.get_quote("000001")

    # 获取K线
    df = tdx.get_kline("000001", period="day", limit=100)

    # 搜索股票
    df = tdx.search_stock("茅台")
"""

__version__ = "0.1.0"
__author__ = "lingzhia"

# 导入所有API函数
from .api import (
    auth,
    # 行情数据
    get_quote,
    get_kline,
    get_minute,
    get_trade,
    search_stock,
    get_stock_info,
    # 批量接口
    batch_quote,
    get_stock_list,
    # K线扩展
    get_kline_history,
    get_kline_all,
    get_kline_all_tdx,
    get_kline_all_ths,
    # 指数
    get_index,
    get_index_all,
    # 分时成交
    get_trade_history,
    get_minute_trade_all,
    get_trade_history_full,
    # ETF
    get_etf_list,
    get_etf_codes,
    # 股票代码
    get_stock_codes,
    # 交易日
    get_workday_info,
    get_workday_range,
    is_workday,
    get_next_workday,
    get_previous_workday,
    # 市场数据
    get_market_count,
    get_market_stats,
    # 收益分析
    get_income,
    # 任务管理
    create_kline_task,
    create_trade_task,
    list_tasks,
    get_task,
    cancel_task,
    # 系统
    health,
    get_server_status,
)

# 导入异常
from .exceptions import (
    TDXError,
    TDXConnectionError,
    TDXAPIError,
    TDXDataError,
    TDXAuthError,
)

# 导入客户端
from .client import Client

__all__ = [
    # 版本
    "__version__",
    # 异常
    "TDXError",
    "TDXConnectionError",
    "TDXAPIError",
    "TDXDataError",
    "TDXAuthError",
    # 客户端
    "Client",
    # 初始化
    "auth",
    # 行情数据
    "get_quote",
    "get_kline",
    "get_minute",
    "get_trade",
    "search_stock",
    "get_stock_info",
    # 批量接口
    "batch_quote",
    "get_stock_list",
    # K线扩展
    "get_kline_history",
    "get_kline_all",
    "get_kline_all_tdx",
    "get_kline_all_ths",
    # 指数
    "get_index",
    "get_index_all",
    # 分时成交
    "get_trade_history",
    "get_minute_trade_all",
    "get_trade_history_full",
    # ETF
    "get_etf_list",
    "get_etf_codes",
    # 股票代码
    "get_stock_codes",
    # 交易日
    "get_workday_info",
    "get_workday_range",
    "is_workday",
    "get_next_workday",
    "get_previous_workday",
    # 市场数据
    "get_market_count",
    "get_market_stats",
    # 收益分析
    "get_income",
    # 任务管理
    "create_kline_task",
    "create_trade_task",
    "list_tasks",
    "get_task",
    "cancel_task",
    # 系统
    "health",
    "get_server_status",
]

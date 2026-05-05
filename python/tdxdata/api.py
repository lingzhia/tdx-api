# -*- coding: utf-8 -*-
"""
tdxdata API函数接口
类jqdata风格的函数式接口
"""

from .config import get_client
from .utils import normalize_date


# ========== 初始化 ==========

def auth():
    """
    初始化连接，类似jqdata.auth()

    Returns:
        Client: 客户端实例
    """
    return get_client()


# ========== 行情数据 ==========

def get_quote(code: str):
    """
    获取五档行情，支持逗号分隔多代码

    Args:
        code: 股票代码，如000001或000001,600519

    Returns:
        DataFrame: 五档行情数据
    """
    return get_client().quote(code)


def get_kline(code: str, period: str = "day", limit: int = 100):
    """
    获取K线数据

    Args:
        code: 股票代码
        period: K线周期 minute1/5/15/30/hour/day/week/month
        limit: 返回条数

    Returns:
        DataFrame: K线数据
    """
    return get_client().kline(code, period, limit)


def get_minute(code: str, date: str = None):
    """
    获取分时数据

    Args:
        code: 股票代码
        date: 日期YYYYMMDD格式，默认当天

    Returns:
        DataFrame: 分时数据
    """
    return get_client().minute(code, date)


def get_trade(code: str, date: str = None):
    """
    获取逐笔成交

    Args:
        code: 股票代码
        date: 日期YYYYMMDD格式，默认当天

    Returns:
        DataFrame: 逐笔成交数据
    """
    return get_client().trade(code, date)


def search_stock(keyword: str):
    """
    搜索股票

    Args:
        keyword: 关键词（代码或名称）

    Returns:
        DataFrame: 搜索结果
    """
    return get_client().search(keyword)


def get_stock_info(code: str):
    """
    获取股票综合信息(五档+K线+分时)

    Args:
        code: 股票代码

    Returns:
        dict: 综合信息
    """
    return get_client().stock_info(code)


# ========== 批量接口 ==========

def batch_quote(codes):
    """
    批量获取行情

    Args:
        codes: 股票代码列表

    Returns:
        dict: 批量行情数据
    """
    return get_client().batch_quote(codes)


def get_stock_list(exchange: str = "all"):
    """
    获取股票列表

    Args:
        exchange: 交易所 sh/sz/bj/all

    Returns:
        dict: 股票列表
    """
    return get_client().stock_list(exchange)


# ========== K线扩展 ==========

def get_kline_history(code: str, period: str = "day",
                      start_date: str = None, end_date: str = None,
                      limit: int = 100):
    """
    获取指定时间范围K线

    Args:
        code: 股票代码
        period: K线周期
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回条数

    Returns:
        DataFrame: K线数据
    """
    return get_client().kline_history(code, period, start_date, end_date, limit)


def get_kline_all(code: str, period: str = "day", limit: int = None):
    """
    获取全量历史K线

    Args:
        code: 股票代码
        period: K线周期
        limit: 返回条数限制

    Returns:
        dict: 全量K线数据
    """
    return get_client().kline_all(code, period, limit)


def get_kline_all_tdx(code: str, period: str = "day", limit: int = None):
    """
    获取通达信原始K线

    Args:
        code: 股票代码
        period: K线周期
        limit: 返回条数限制

    Returns:
        dict: 通达信原始K线
    """
    return get_client().kline_all_tdx(code, period, limit)


def get_kline_all_ths(code: str, period: str = "day", limit: int = None):
    """
    获取同花顺前复权K线

    Args:
        code: 股票代码
        period: K线周期(仅支持day/week/month)
        limit: 返回条数限制

    Returns:
        dict: 同花顺前复权K线
    """
    return get_client().kline_all_ths(code, period, limit)


# ========== 指数 ==========

def get_index(code: str, period: str = "day"):
    """
    获取指数K线

    Args:
        code: 指数代码，如sh000001
        period: K线周期

    Returns:
        DataFrame: 指数K线
    """
    return get_client().index(code, period)


def get_index_all(code: str, period: str = "day", limit: int = None):
    """
    获取指数全量K线

    Args:
        code: 指数代码
        period: K线周期
        limit: 返回条数限制

    Returns:
        dict: 指数全量K线
    """
    return get_client().index_all(code, period, limit)


# ========== 分时成交 ==========

def get_trade_history(code: str, date: str, start: int = 0, count: int = 2000):
    """
    历史分时成交(分页)

    Args:
        code: 股票代码
        date: 交易日期YYYYMMDD
        start: 起始游标
        count: 返回条数

    Returns:
        dict: 分时成交数据
    """
    return get_client().trade_history(code, date, start, count)


def get_minute_trade_all(code: str, date: str = None):
    """
    全天分时成交

    Args:
        code: 股票代码
        date: 日期YYYYMMDD，默认当天

    Returns:
        dict: 全天分时成交
    """
    return get_client().minute_trade_all(code, date)


def get_trade_history_full(code: str, before: str = None, limit: int = None):
    """
    上市以来全部分时成交

    Args:
        code: 股票代码
        before: 截止日期YYYYMMDD
        limit: 返回条数限制

    Returns:
        dict: 全部分时成交
    """
    return get_client().trade_history_full(code, before, limit)


# ========== ETF ==========

def get_etf_list(exchange: str = None, limit: int = None):
    """
    获取ETF列表

    Args:
        exchange: 交易所 sh/sz
        limit: 返回条数

    Returns:
        dict: ETF列表
    """
    return get_client().etf_list(exchange, limit)


def get_etf_codes(limit: int = None, prefix: bool = True):
    """
    获取ETF代码列表

    Args:
        limit: 返回条数
        prefix: 是否包含交易所前缀

    Returns:
        dict: ETF代码列表
    """
    return get_client().etf_codes(limit, prefix)


# ========== 股票代码 ==========

def get_stock_codes(limit: int = None, prefix: bool = True):
    """
    获取股票代码列表

    Args:
        limit: 返回条数
        prefix: 是否包含交易所前缀

    Returns:
        dict: 股票代码列表
    """
    return get_client().stock_codes(limit, prefix)


# ========== 交易日 ==========

def get_workday_info(date: str = None, count: int = 1):
    """
    查询交易日信息

    Args:
        date: 日期YYYYMMDD，默认当天
        count: 返回前后交易日数量

    Returns:
        dict: 交易日信息
    """
    return get_client().workday_info(date, count)


def get_workday_range(start: str, end: str):
    """
    获取交易日范围

    Args:
        start: 起始日期YYYYMMDD
        end: 结束日期YYYYMMDD

    Returns:
        dict: 交易日范围
    """
    return get_client().workday_range(start, end)


def is_workday(date: str = None) -> bool:
    """
    判断是否交易日

    Args:
        date: 日期YYYYMMDD，默认当天

    Returns:
        bool: 是否交易日
    """
    info = get_client().workday_info(date)
    return info.get('data', {}).get('is_workday', False)


def get_next_workday(date: str = None, count: int = 1) -> list:
    """
    获取下一个交易日

    Args:
        date: 日期YYYYMMDD，默认当天
        count: 返回数量

    Returns:
        list: 下一个交易日列表
    """
    info = get_client().workday_info(date, count)
    return info.get('data', {}).get('next', [])


def get_previous_workday(date: str = None, count: int = 1) -> list:
    """
    获取上一个交易日

    Args:
        date: 日期YYYYMMDD，默认当天
        count: 返回数量

    Returns:
        list: 上一个交易日列表
    """
    info = get_client().workday_info(date, count)
    return info.get('data', {}).get('previous', [])


# ========== 市场数据 ==========

def get_market_count():
    """
    获取市场证券数量

    Returns:
        dict: 市场证券数量
    """
    return get_client().market_count()


def get_market_stats():
    """
    获取市场统计

    Returns:
        dict: 市场统计
    """
    return get_client().market_stats()


# ========== 收益分析 ==========

def get_income(code: str, start_date: str, days: str = "5,10,20,60,120"):
    """
    计算收益区间

    Args:
        code: 股票代码
        start_date: 基准日期YYYYMMDD
        days: 天数偏移，逗号分隔

    Returns:
        dict: 收益区间数据
    """
    return get_client().income(code, start_date, days)


# ========== 任务管理 ==========

def create_kline_task(codes=None, tables=None, limit: int = 1, start_date: str = None):
    """
    创建K线入库任务

    Args:
        codes: 股票代码列表，默认全部
        tables: K线类型，如["day", "week"]
        limit: 并发数
        start_date: 起始日期

    Returns:
        str: 任务ID
    """
    return get_client().create_kline_task(codes, tables, limit, start_date)


def create_trade_task(code: str, start_year: int = 2000, end_year: int = None):
    """
    创建分时成交入库任务

    Args:
        code: 股票代码
        start_year: 起始年份
        end_year: 结束年份

    Returns:
        str: 任务ID
    """
    return get_client().create_trade_task(code, start_year, end_year)


def list_tasks():
    """
    获取任务列表

    Returns:
        list: 任务列表
    """
    return get_client().list_tasks()


def get_task(task_id: str):
    """
    获取任务详情

    Args:
        task_id: 任务ID

    Returns:
        dict: 任务详情
    """
    return get_client().get_task(task_id)


def cancel_task(task_id: str):
    """
    取消任务

    Args:
        task_id: 任务ID

    Returns:
        dict: 操作结果
    """
    return get_client().cancel_task(task_id)


# ========== 系统 ==========

def health():
    """
    健康检查

    Returns:
        dict: 健康状态
    """
    return get_client().health()


def get_server_status():
    """
    获取服务状态

    Returns:
        dict: 服务状态
    """
    return get_client().server_status()

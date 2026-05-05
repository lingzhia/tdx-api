# -*- coding: utf-8 -*-
"""
tdxdata API客户端核心实现
封装全部32个API接口
"""

import requests
from typing import List, Dict, Optional, Union
import pandas as pd

from .config import BASE_URL, TIMEOUT
from .exceptions import TDXConnectionError, TDXAPIError
from .utils import (
    build_quote_df, build_kline_df, build_minute_df,
    build_trade_df, build_search_df,
    normalize_date
)


class Client:
    """TDX API客户端"""

    def __init__(self, base_url: str = BASE_URL, timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _get(self, path: str, params: Dict = None, check_code: bool = True) -> Dict:
        """GET请求

        Args:
            path: API路径
            params: 请求参数
            check_code: 是否检查code字段，某些接口(如/health)无code字段
        """
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if check_code and data.get('code') != 0:
                raise TDXAPIError(data.get('code'), data.get('message', ''))
            return data
        except requests.exceptions.ConnectionError as e:
            raise TDXConnectionError(f"连接失败: {e}")
        except requests.exceptions.Timeout as e:
            raise TDXConnectionError(f"请求超时: {e}")

    def _post(self, path: str, json: Dict = None) -> Dict:
        """POST请求"""
        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(url, json=json, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if data.get('code') != 0:
                raise TDXAPIError(data.get('code'), data.get('message', ''))
            return data
        except requests.exceptions.ConnectionError as e:
            raise TDXConnectionError(f"连接失败: {e}")
        except requests.exceptions.Timeout as e:
            raise TDXConnectionError(f"请求超时: {e}")

    # ========== 1. 获取五档行情 ==========

    def quote(self, code: str) -> pd.DataFrame:
        """
        获取五档行情

        Args:
            code: 股票代码，支持逗号分隔多代码

        Returns:
            DataFrame: 包含五档行情数据
        """
        data = self._get("/api/quote", {"code": code})
        return build_quote_df(data.get('data', []))

    def get_quote(self, code: str) -> pd.DataFrame:
        """get_quote的别名"""
        return self.quote(code)

    # ========== 2. 获取K线数据 ==========

    def kline(self, code: str, period: str = "day", limit: int = 100) -> pd.DataFrame:
        """
        获取K线数据

        Args:
            code: 股票代码
            period: K线周期 minute1/5/15/30/hour/day/week/month
            limit: 返回条数

        Returns:
            DataFrame: K线数据
        """
        data = self._get("/api/kline", {"code": code, "type": period, "limit": limit})
        return build_kline_df(data.get('data', {}).get('List', []))

    def get_kline(self, code: str, period: str = "day", limit: int = 100) -> pd.DataFrame:
        """get_kline的别名"""
        return self.kline(code, period, limit)

    # ========== 3. 获取分时数据 ==========

    def minute(self, code: str, date: str = None) -> pd.DataFrame:
        """
        获取分时数据

        Args:
            code: 股票代码
            date: 日期YYYYMMDD格式，默认当天

        Returns:
            DataFrame: 分时数据
        """
        params = {"code": code}
        if date:
            params["date"] = normalize_date(date)
        data = self._get("/api/minute", params)
        return build_minute_df(data.get('data', {}).get('List', []))

    def get_minute(self, code: str, date: str = None) -> pd.DataFrame:
        """get_minute的别名"""
        return self.minute(code, date)

    # ========== 4. 获取分时成交 ==========

    def trade(self, code: str, date: str = None) -> pd.DataFrame:
        """
        获取逐笔成交

        Args:
            code: 股票代码
            date: 日期YYYYMMDD格式，默认当天

        Returns:
            DataFrame: 逐笔成交数据
        """
        params = {"code": code}
        if date:
            params["date"] = normalize_date(date)
        data = self._get("/api/trade", params)
        return build_trade_df(data.get('data', {}).get('List', []))

    def get_trade(self, code: str, date: str = None) -> pd.DataFrame:
        """get_trade的别名"""
        return self.trade(code, date)

    # ========== 5. 搜索股票 ==========

    def search(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票

        Args:
            keyword: 关键词（代码或名称）

        Returns:
            DataFrame: 搜索结果
        """
        data = self._get("/api/search", {"keyword": keyword})
        return build_search_df(data.get('data', []))

    def search_stock(self, keyword: str) -> pd.DataFrame:
        """search_stock的别名"""
        return self.search(keyword)

    # ========== 6. 获取股票综合信息 ==========

    def stock_info(self, code: str) -> Dict:
        """
        获取股票综合信息

        Args:
            code: 股票代码

        Returns:
            dict: 包含quote、kline_day、minute
        """
        return self._get("/api/stock-info", {"code": code})

    def get_stock_info(self, code: str) -> Dict:
        """get_stock_info的别名"""
        return self.stock_info(code)

    # ========== 7. 获取股票列表 ==========

    def stock_list(self, exchange: str = "all") -> Dict:
        """
        获取股票列表

        Args:
            exchange: 交易所 sh/sz/bj/all

        Returns:
            dict: 股票列表
        """
        return self._get("/api/codes", {"exchange": exchange})

    def get_stock_list(self, exchange: str = "all") -> Dict:
        """get_stock_list的别名"""
        return self.stock_list(exchange)

    # ========== 8. 批量获取行情 ==========

    def batch_quote(self, codes: List[str]) -> Dict:
        """
        批量获取行情

        Args:
            codes: 股票代码列表

        Returns:
            dict: 批量行情数据
        """
        return self._post("/api/batch-quote", {"codes": codes})

    # ========== 9. 获取历史K线 ==========

    def kline_history(self, code: str, period: str = "day",
                      start_date: str = None, end_date: str = None,
                      limit: int = 100) -> pd.DataFrame:
        """
        获取指定时间范围K线

        Args:
            code: 股票代码
            period: K线周期
            start_date: 开始日期YYYYMMDD
            end_date: 结束日期YYYYMMDD
            limit: 返回条数

        Returns:
            DataFrame: K线数据
        """
        params = {"code": code, "type": period, "limit": limit}
        if start_date:
            params["start_date"] = normalize_date(start_date)
        if end_date:
            params["end_date"] = normalize_date(end_date)
        data = self._get("/api/kline-history", params)
        return build_kline_df(data.get('data', {}).get('List', []))

    def get_kline_history(self, code: str, period: str = "day",
                          start_date: str = None, end_date: str = None,
                          limit: int = 100) -> pd.DataFrame:
        """get_kline_history的别名"""
        return self.kline_history(code, period, start_date, end_date, limit)

    # ========== 10. 获取指数数据 ==========

    def index(self, code: str, period: str = "day") -> pd.DataFrame:
        """
        获取指数K线

        Args:
            code: 指数代码，如sh000001
            period: K线周期

        Returns:
            DataFrame: 指数K线
        """
        data = self._get("/api/index", {"code": code, "type": period})
        return build_kline_df(data.get('data', {}).get('List', []))

    def get_index(self, code: str, period: str = "day") -> pd.DataFrame:
        """get_index的别名"""
        return self.index(code, period)

    # ========== 11. 获取服务状态 ==========

    def server_status(self) -> Dict:
        """获取服务状态"""
        return self._get("/api/server-status")

    def get_server_status(self) -> Dict:
        """get_server_status的别名"""
        return self.server_status()

    # ========== 12. 创建K线入库任务 ==========

    def create_kline_task(self, codes: List[str] = None,
                          tables: List[str] = None,
                          limit: int = 1,
                          start_date: str = None,
                          directory: str = None) -> str:
        """
        创建K线入库任务

        Args:
            codes: 股票代码列表，默认全部
            tables: K线类型，如["day", "week"]
            limit: 并发数
            start_date: 起始日期
            directory: 存储目录

        Returns:
            str: 任务ID
        """
        payload = {}
        if codes:
            payload["codes"] = codes
        if tables:
            payload["tables"] = tables
        if limit:
            payload["limit"] = limit
        if start_date:
            payload["start_date"] = start_date
        if directory:
            payload["dir"] = directory
        data = self._post("/api/tasks/pull-kline", payload or {})
        return data.get('data', {}).get('task_id', '')

    # ========== 13. 创建分时成交入库任务 ==========

    def create_trade_task(self, code: str,
                          start_year: int = 2000,
                          end_year: int = None,
                          directory: str = None) -> str:
        """
        创建分时成交入库任务

        Args:
            code: 股票代码
            start_year: 起始年份
            end_year: 结束年份
            directory: 存储目录

        Returns:
            str: 任务ID
        """
        payload = {"code": code, "start_year": start_year}
        if end_year:
            payload["end_year"] = end_year
        if directory:
            payload["dir"] = directory
        data = self._post("/api/tasks/pull-trade", payload)
        return data.get('data', {}).get('task_id', '')

    # ========== 14. 获取任务列表 ==========

    def list_tasks(self) -> List[Dict]:
        """获取任务列表"""
        data = self._get("/api/tasks")
        return data.get('data', [])

    # ========== 15. 获取任务详情 ==========

    def get_task(self, task_id: str) -> Dict:
        """获取任务详情"""
        return self._get(f"/api/tasks/{task_id}")

    # ========== 16. 取消任务 ==========

    def cancel_task(self, task_id: str) -> Dict:
        """取消任务"""
        return self._post(f"/api/tasks/{task_id}/cancel")

    # ========== 17. 获取ETF列表 ==========

    def etf_list(self, exchange: str = None, limit: int = None) -> Dict:
        """
        获取ETF列表

        Args:
            exchange: 交易所 sh/sz
            limit: 返回条数

        Returns:
            dict: ETF列表
        """
        params = {}
        if exchange:
            params["exchange"] = exchange
        if limit:
            params["limit"] = limit
        return self._get("/api/etf", params)

    def get_etf_list(self, exchange: str = None, limit: int = None) -> Dict:
        """get_etf_list的别名"""
        return self.etf_list(exchange, limit)

    # ========== 18. 获取历史分时成交(分页) ==========

    def trade_history(self, code: str, date: str,
                       start: int = 0, count: int = 2000) -> Dict:
        """
        获取历史分时成交(分页)

        Args:
            code: 股票代码
            date: 交易日期YYYYMMDD
            start: 起始游标
            count: 返回条数

        Returns:
            dict: 分时成交数据
        """
        params = {
            "code": code,
            "date": normalize_date(date),
            "start": start,
            "count": count
        }
        return self._get("/api/trade-history", params)

    def get_trade_history(self, code: str, date: str,
                           start: int = 0, count: int = 2000) -> Dict:
        """get_trade_history的别名"""
        return self.trade_history(code, date, start, count)

    # ========== 19. 获取全天分时成交 ==========

    def minute_trade_all(self, code: str, date: str = None) -> Dict:
        """
        获取全天分时成交

        Args:
            code: 股票代码
            date: 日期YYYYMMDD，默认当天

        Returns:
            dict: 全天分时成交
        """
        params = {"code": code}
        if date:
            params["date"] = normalize_date(date)
        return self._get("/api/minute-trade-all", params)

    def get_minute_trade_all(self, code: str, date: str = None) -> Dict:
        """get_minute_trade_all的别名"""
        return self.minute_trade_all(code, date)

    # ========== 20. 查询交易日信息 ==========

    def workday_info(self, date: str = None, count: int = 1) -> Dict:
        """
        查询交易日信息

        Args:
            date: 日期YYYYMMDD，默认当天
            count: 返回前后交易日数量

        Returns:
            dict: 交易日信息
        """
        params = {"count": count}
        if date:
            params["date"] = normalize_date(date)
        return self._get("/api/workday", params)

    def get_workday_info(self, date: str = None, count: int = 1) -> Dict:
        """get_workday_info的别名"""
        return self.workday_info(date, count)

    # ========== 21. 获取市场证券数量 ==========

    def market_count(self) -> Dict:
        """获取市场证券数量"""
        return self._get("/api/market-count")

    def get_market_count(self) -> Dict:
        """get_market_count的别名"""
        return self.market_count()

    # ========== 22. 获取股票代码列表 ==========

    def stock_codes(self, limit: int = None, prefix: bool = True) -> Dict:
        """
        获取股票代码列表

        Args:
            limit: 返回条数
            prefix: 是否包含交易所前缀

        Returns:
            dict: 股票代码列表
        """
        params = {"prefix": str(prefix).lower()}
        if limit:
            params["limit"] = limit
        return self._get("/api/stock-codes", params)

    def get_stock_codes(self, limit: int = None, prefix: bool = True) -> Dict:
        """get_stock_codes的别名"""
        return self.stock_codes(limit, prefix)

    # ========== 23. 获取ETF代码列表 ==========

    def etf_codes(self, limit: int = None, prefix: bool = True) -> Dict:
        """
        获取ETF代码列表

        Args:
            limit: 返回条数
            prefix: 是否包含交易所前缀

        Returns:
            dict: ETF代码列表
        """
        params = {"prefix": str(prefix).lower()}
        if limit:
            params["limit"] = limit
        return self._get("/api/etf-codes", params)

    def get_etf_codes(self, limit: int = None, prefix: bool = True) -> Dict:
        """get_etf_codes的别名"""
        return self.etf_codes(limit, prefix)

    # ========== 24. 获取全量历史K线 ==========

    def kline_all(self, code: str, period: str = "day", limit: int = None) -> Dict:
        """
        获取全量历史K线

        Args:
            code: 股票代码
            period: K线周期
            limit: 返回条数限制

        Returns:
            dict: 全量K线数据
        """
        params = {"code": code, "type": period}
        if limit:
            params["limit"] = limit
        return self._get("/api/kline-all", params)

    def get_kline_all(self, code: str, period: str = "day", limit: int = None) -> Dict:
        """get_kline_all的别名"""
        return self.kline_all(code, period, limit)

    # ========== 25. 获取指数全量K线 ==========

    def index_all(self, code: str, period: str = "day", limit: int = None) -> Dict:
        """
        获取指数全量K线

        Args:
            code: 指数代码
            period: K线周期
            limit: 返回条数限制

        Returns:
            dict: 指数全量K线
        """
        params = {"code": code, "type": period}
        if limit:
            params["limit"] = limit
        return self._get("/api/index/all", params)

    def get_index_all(self, code: str, period: str = "day", limit: int = None) -> Dict:
        """get_index_all的别名"""
        return self.index_all(code, period, limit)

    # ========== 26. 获取上市以来全部分时成交 ==========

    def trade_history_full(self, code: str, before: str = None,
                           limit: int = None) -> Dict:
        """
        获取上市以来全部分时成交

        Args:
            code: 股票代码
            before: 截止日期YYYYMMDD
            limit: 返回条数限制

        Returns:
            dict: 全部分时成交
        """
        params = {"code": code}
        if before:
            params["before"] = normalize_date(before)
        if limit:
            params["limit"] = limit
        return self._get("/api/trade-history/full", params)

    def get_trade_history_full(self, code: str, before: str = None,
                                limit: int = None) -> Dict:
        """get_trade_history_full的别名"""
        return self.trade_history_full(code, before, limit)

    # ========== 27. 获取交易日范围 ==========

    def workday_range(self, start: str, end: str) -> Dict:
        """
        获取交易日范围

        Args:
            start: 起始日期YYYYMMDD
            end: 结束日期YYYYMMDD

        Returns:
            dict: 交易日范围
        """
        return self._get("/api/workday/range", {
            "start": normalize_date(start),
            "end": normalize_date(end)
        })

    def get_workday_range(self, start: str, end: str) -> Dict:
        """get_workday_range的别名"""
        return self.workday_range(start, end)

    # ========== 28. 计算收益区间 ==========

    def income(self, code: str, start_date: str,
               days: str = "5,10,20,60,120") -> Dict:
        """
        计算收益区间

        Args:
            code: 股票代码
            start_date: 基准日期YYYYMMDD
            days: 天数偏移，逗号分隔

        Returns:
            dict: 收益区间数据
        """
        return self._get("/api/income", {
            "code": code,
            "start_date": normalize_date(start_date),
            "days": days
        })

    def get_income(self, code: str, start_date: str,
                    days: str = "5,10,20,60,120") -> Dict:
        """get_income的别名"""
        return self.income(code, start_date, days)

    # ========== 29. 获取通达信原始K线 ==========

    def kline_all_tdx(self, code: str, period: str = "day",
                      limit: int = None) -> Dict:
        """
        获取通达信原始K线

        Args:
            code: 股票代码
            period: K线周期
            limit: 返回条数限制

        Returns:
            dict: 通达信原始K线
        """
        params = {"code": code, "type": period}
        if limit:
            params["limit"] = limit
        return self._get("/api/kline-all/tdx", params)

    def get_kline_all_tdx(self, code: str, period: str = "day",
                           limit: int = None) -> Dict:
        """get_kline_all_tdx的别名"""
        return self.kline_all_tdx(code, period, limit)

    # ========== 30. 获取同花顺前复权K线 ==========

    def kline_all_ths(self, code: str, period: str = "day",
                      limit: int = None) -> Dict:
        """
        获取同花顺前复权K线

        Args:
            code: 股票代码
            period: K线周期(仅支持day/week/month)
            limit: 返回条数限制

        Returns:
            dict: 同花顺前复权K线
        """
        params = {"code": code, "type": period}
        if limit:
            params["limit"] = limit
        return self._get("/api/kline-all/ths", params)

    def get_kline_all_ths(self, code: str, period: str = "day",
                           limit: int = None) -> Dict:
        """get_kline_all_ths的别名"""
        return self.kline_all_ths(code, period, limit)

    # ========== 31. 健康检查 ==========

    def health(self) -> Dict:
        """健康检查"""
        return self._get("/api/health", check_code=False)

    # ========== 32. 获取市场统计 ==========

    def market_stats(self) -> Dict:
        """获取市场统计"""
        return self._get("/api/market-stats")

    def get_market_stats(self) -> Dict:
        """get_market_stats的别名"""
        return self.market_stats()

# -*- coding: utf-8 -*-
"""
tdxdata 工具函数
"""

from typing import Any, Dict, List, Optional
import pandas as pd


# ========== 单位转换 ==========

def li_to_yuan(li: int) -> float:
    """厘转元（API返回价格单位是厘）"""
    return li / 1000.0


def yuan_to_li(yuan: float) -> int:
    """元转厘"""
    return int(yuan * 1000)


def hand_to_share(hand: int) -> int:
    """手转股（1手=100股）"""
    return hand * 100


def share_to_hand(share: int) -> int:
    """股转手"""
    return share // 100


def li_amount_to_yuan(li: int) -> float:
    """厘金额转元成交额"""
    return li / 1000.0


# ========== DataFrame构建 ==========

def build_quote_df(data: List[Dict]) -> pd.DataFrame:
    """构建行情DataFrame"""
    if not data:
        return pd.DataFrame()

    records = []
    for item in data:
        record = {
            'code': item.get('Code', ''),
            'exchange': _exchange_code(item.get('Exchange', 0)),
            'last': li_to_yuan(item.get('K', {}).get('Last', 0)),
            'open': li_to_yuan(item.get('K', {}).get('Open', 0)),
            'high': li_to_yuan(item.get('K', {}).get('High', 0)),
            'low': li_to_yuan(item.get('K', {}).get('Low', 0)),
            'close': li_to_yuan(item.get('K', {}).get('Close', 0)),
            'volume': item.get('TotalHand', 0),
            'amount': li_amount_to_yuan(item.get('Amount', 0)),
            'inside_dish': item.get('InsideDish', 0),
            'outer_disc': item.get('OuterDisc', 0),
        }

        # 买五档
        for i, level in enumerate(item.get('BuyLevel', [])[:5]):
            record[f'buy{i+1}'] = li_to_yuan(level.get('Price', 0))
            record[f'buy{i+1}_vol'] = level.get('Number', 0) // 100

        # 卖五档
        for i, level in enumerate(item.get('SellLevel', [])[:5]):
            record[f'sell{i+1}'] = li_to_yuan(level.get('Price', 0))
            record[f'sell{i+1}_vol'] = level.get('Number', 0) // 100

        records.append(record)

    df = pd.DataFrame(records)
    return df


def build_kline_df(data: List[Dict]) -> pd.DataFrame:
    """构建K线DataFrame"""
    if not data:
        return pd.DataFrame()

    records = []
    for item in data:
        record = {
            'time': pd.to_datetime(item.get('Time')),
            'open': li_to_yuan(item.get('Open', 0)),
            'high': li_to_yuan(item.get('High', 0)),
            'low': li_to_yuan(item.get('Low', 0)),
            'close': li_to_yuan(item.get('Close', 0)),
            'volume': item.get('Volume', 0),
            'amount': li_amount_to_yuan(item.get('Amount', 0)),
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def build_minute_df(data: List[Dict]) -> pd.DataFrame:
    """构建分时DataFrame"""
    if not data:
        return pd.DataFrame()

    records = []
    for item in data:
        record = {
            'time': item.get('Time', ''),
            'price': li_to_yuan(item.get('Price', 0)),
            'volume': item.get('Number', 0),
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def build_trade_df(data: List[Dict]) -> pd.DataFrame:
    """构建逐笔成交DataFrame"""
    if not data:
        return pd.DataFrame()

    records = []
    for item in data:
        record = {
            'time': item.get('Time', ''),
            'price': li_to_yuan(item.get('Price', 0)),
            'volume': item.get('Volume', 0),
            'status': item.get('Status', 0),  # 0=买入,1=卖出,2=中性
            'number': item.get('Number', 0),  # 成交单数
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def build_search_df(data: List[Dict]) -> pd.DataFrame:
    """构建搜索结果DataFrame"""
    if not data:
        return pd.DataFrame()

    records = []
    for item in data:
        record = {
            'code': item.get('code', ''),
            'name': item.get('name', ''),
            'exchange': item.get('exchange', ''),
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


# ========== 辅助函数 ==========

def _exchange_code(code: int) -> str:
    """交易所代码转换"""
    mapping = {0: 'sh', 1: 'sz', 2: 'bj'}
    return mapping.get(code, 'unknown')


def normalize_date(date: str = None) -> str:
    """标准化日期格式"""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%Y%m%d")
    # 移除横杠
    return date.replace('-', '')


def check_response(resp: Dict) -> None:
    """检查API响应"""
    if resp.get('code') != 0:
        raise Exception(f"API错误 [{resp.get('code')}]: {resp.get('message', '未知错误')}")

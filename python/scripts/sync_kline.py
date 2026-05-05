#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX 1分钟K线数据同步脚本 - 高并发版
使用asyncio并发获取数据

Usage:
    python sync_kline.py --all              # 同步全市场
    python sync_kline.py --code 000001      # 测试单只
"""

import sys
import os
import json
import time
import signal
import logging
import argparse
import asyncio
from datetime import datetime
from typing import List, Dict, Tuple

import aiohttp

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tdxdata as tdx
from tdxdata.clickhouse import ClickHouseClient

# ============== 配置 ==============
PROGRESS_FILE = "sync_progress.json"
LOG_FILE = "sync_kline.log"

# TDX API 配置
TDX_HOST = "100.107.142.74"
TDX_PORT = 8080
TDX_BASE_URL = f"http://{TDX_HOST}:{TDX_PORT}"

# 并发配置
CONCURRENCY = 100  # 并发请求数

# ============== 日志配置 ==============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ============== 工具函数 ==============

def parse_time(ts) -> str:
    """解析时间为ClickHouse格式"""
    if isinstance(ts, str):
        ts = ts.replace('+08:00', '').replace('T', ' ')
        return ts[:19]
    if hasattr(ts, 'strftime'):
        try:
            ts = ts.replace(tzinfo=None)
            return ts.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    return str(ts)[:19]


def get_exchange(code: str) -> str:
    """根据代码判断交易所"""
    if code.startswith(('8', '4')):
        return 'bj'
    elif code.startswith('6'):
        return 'sh'
    else:
        return 'sz'


# ============== 异步获取函数 ==============

async def fetch_kline(session: aiohttp.ClientSession, code: str, limit: int = 8000) -> Tuple[str, int, List[Dict]]:
    """异步获取单只股票K线"""
    url = f"{TDX_BASE_URL}/api/kline"
    params = {"code": code, "type": "minute1", "limit": limit}

    try:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return code, 0, []

            data = await resp.json()
            if data.get('code') != 0:
                return code, 0, []

            # API返回结构: {"data": {"Count": N, "List": [...]}}
            items = data.get('data', {}).get('List', [])
            if not items:
                return code, 0, []

            # 解析数据
            records = []
            exchange = get_exchange(code)

            for item in items:
                try:
                    # API返回的价格单位是厘
                    close = int(item.get('Close', 0))
                    if close <= 0:
                        continue

                    time_str = item.get('Time', '')
                    if not time_str:
                        continue

                    record = {
                        'code': code,
                        'exchange': exchange,
                        'time': parse_time(time_str),
                        'open': int(item.get('Open', 0)),
                        'high': int(item.get('High', 0)),
                        'low': int(item.get('Low', 0)),
                        'close': close,
                        'volume': int(item.get('Volume', 0)),
                        'amount': int(item.get('Amount', 0)),
                    }
                    records.append(record)
                except:
                    continue

            return code, len(records), records
    except Exception as e:
        return code, 0, []


# ============== 主同步逻辑 ==============

async def worker(worker_id: int, codes: List[str], ch_client: ClickHouseClient,
                progress: Dict, progress_lock: asyncio.Lock, sem: asyncio.Semaphore):
    """工作协程"""
    async with aiohttp.ClientSession() as session:
        for code in codes:
            async with sem:  # 限流
                code, count, records = await fetch_kline(session, code)

                async with progress_lock:
                    progress["synced_codes"] += 1
                    progress["last_code"] = code
                    if count > 0:
                        progress["synced_records"] += count

                    # 输出进度
                    if progress["synced_codes"] % 500 == 0:
                        pct = progress["synced_codes"] / progress["total_codes"] * 100
                        logger.info(f"进度: {progress['synced_codes']}/{progress['total_codes']} ({pct:.1f}%), 已同步 {progress['synced_records']:,} 条")

                if records:
                    try:
                        ch_client.insert_kline_1min(records)
                    except Exception as e:
                        logger.error(f"写入 {code} 失败: {e}")


async def sync_market(workers: int = CONCURRENCY):
    """同步全市场数据"""
    # 获取股票列表（使用tdxdata）
    logger.info("获取股票列表...")
    result = tdx.get_stock_list("all")
    if result.get('code') != 0:
        logger.error("获取股票列表失败")
        return

    codes_data = result.get('data', {}).get('codes', [])
    codes = [c.get('code', '') if isinstance(c, dict) else str(c) for c in codes_data]
    codes = [c for c in codes if c]
    logger.info(f"获取到 {len(codes)} 只股票")

    # 初始化
    ch_client = ClickHouseClient()
    if not ch_client.test_connection():
        raise ConnectionError("ClickHouse连接失败")
    logger.info("ClickHouse连接成功")

    # 进度
    progress = {
        "synced_codes": 0,
        "total_codes": len(codes),
        "synced_records": 0,
        "last_code": ""
    }
    progress_lock = asyncio.Lock()
    sem = asyncio.Semaphore(workers)  # 限制并发数

    # 分片
    chunk_size = max(1, len(codes) // workers)
    chunks = [codes[i:i+chunk_size] for i in range(0, len(codes), chunk_size)]

    logger.info(f"使用 {workers} 个协程并发处理...")

    # 执行
    tasks = [worker(i, chunk, ch_client, progress, progress_lock, sem) for i, chunk in enumerate(chunks)]
    await asyncio.gather(*tasks)

    logger.info(f"同步完成: 共 {len(codes)} 只股票, {progress['synced_records']:,} 条记录")


async def sync_single(code: str):
    """同步单只股票"""
    logger.info(f"测试同步单只股票: {code}")

    async with aiohttp.ClientSession() as session:
        code, count, records = await fetch_kline(session, code)
        logger.info(f"获取到 {count} 条数据")

        if records:
            ch_client = ClickHouseClient()
            inserted = ch_client.insert_kline_1min(records)
            logger.info(f"写入 {inserted} 条到ClickHouse")

            count_result = ch_client.get_count(code)
            logger.info(f"股票 {code} 在库中共有 {count_result} 条")


# ============== 主函数 ==============

def main():
    parser = argparse.ArgumentParser(description='TDX 1分钟K线同步工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='同步全量')
    group.add_argument('--code', help='测试用：同步单只股票')
    parser.add_argument('--workers', type=int, default=CONCURRENCY, help=f'并发数 (默认{CONCURRENCY})')

    args = parser.parse_args()

    try:
        if args.code:
            asyncio.run(sync_single(args.code))
        else:
            asyncio.run(sync_market(args.workers))
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"同步失败: {e}")


if __name__ == "__main__":
    main()
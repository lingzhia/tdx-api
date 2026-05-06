#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX 1分钟K线数据同步脚本
支持全量同步和增量同步

Usage:
    # 首次全量同步（会覆盖现有数据，用--resume可断点续传）
    python sync_kline.py --full

    # 增量同步（只获取最新数据，追加到现有数据）
    python sync_kline.py --incremental

    # 单只股票测试
    python sync_kline.py --code 000001

    # 定时增量同步（建议crontab每5分钟运行一次）
    # */5 * * * * cd /path/to && python sync_kline.py --incremental
"""

import sys
import os
import json
import time
import logging
import argparse
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

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
CONCURRENCY = 50  # 并发请求数

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


# ============== ClickHouse 工具 ==============

class CHHelper:
    """ClickHouse辅助工具"""

    @staticmethod
    def get_latest_time(ch_client: ClickHouseClient, code: str = None) -> Optional[datetime]:
        """获取某股票或全局最新的K线时间"""
        if code:
            sql = f"SELECT max(time) FROM LingQuant.kline_1min WHERE code = '{code}'"
        else:
            sql = "SELECT max(time) FROM LingQuant.kline_1min"
        result = ch_client._execute(sql)
        if result and result.strip():
            try:
                return datetime.fromisoformat(result.strip().replace('+08:00', ''))
            except:
                pass
        return None

    @staticmethod
    def get_code_latest_times(ch_client: ClickHouseClient) -> Dict[str, datetime]:
        """获取所有股票的最新K线时间"""
        sql = """
        SELECT code, max(time) as latest
        FROM LingQuant.kline_1min
        GROUP BY code
        """
        result = ch_client._execute(sql)
        if not result:
            return {}

        times = {}
        for line in result.strip().split('\n')[1:]:  # 跳过表头
            parts = line.split('\t')
            if len(parts) >= 2 and parts[0] and parts[1]:
                try:
                    times[parts[0]] = datetime.fromisoformat(parts[1].replace('+08:00', ''))
                except:
                    pass
        return times

    @staticmethod
    def count_code(ch_client: ClickHouseClient, code: str) -> int:
        """获取某股票的数据条数"""
        sql = f"SELECT count() FROM LingQuant.kline_1min WHERE code = '{code}'"
        result = ch_client._execute(sql)
        if result:
            try:
                return int(result.strip())
            except:
                pass
        return 0


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

            items = data.get('data', {}).get('List', [])
            if not items:
                return code, 0, []

            records = []
            exchange = get_exchange(code)

            for item in items:
                try:
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


def filter_new_records(records: List[Dict], latest_time: Optional[datetime]) -> List[Dict]:
    """过滤出比latest_time更新的记录"""
    if latest_time is None:
        return records

    new_records = []
    for r in records:
        try:
            rec_time = datetime.fromisoformat(r['time'].replace('+08:00', ''))
            if rec_time > latest_time:
                new_records.append(r)
        except:
            new_records.append(r)  # 解析失败时保留
    return new_records


# ============== 主同步逻辑 ==============

async def worker(worker_id: int, codes: List[str], ch_client: ClickHouseClient,
                progress: Dict, progress_lock: asyncio.Lock, sem: asyncio.Semaphore,
                code_latest_times: Dict[str, datetime]):
    """工作协程"""
    async with aiohttp.ClientSession() as session:
        for code in codes:
            async with sem:
                code, count, records = await fetch_kline(session, code)

                # 增量同步：只保留比本地更新的数据
                latest_time = code_latest_times.get(code)
                if latest_time:
                    new_records = filter_new_records(records, latest_time)
                    skip_count = len(records) - len(new_records)
                else:
                    new_records = records
                    skip_count = 0

                async with progress_lock:
                    progress["synced_codes"] += 1
                    progress["last_code"] = code
                    if len(new_records) > 0:
                        progress["synced_records"] += len(new_records)
                        progress["new_records"] += len(new_records)
                    progress["skip_records"] += skip_count

                    if progress["synced_codes"] % 100 == 0:
                        pct = progress["synced_codes"] / progress["total_codes"] * 100
                        logger.info(f"进度: {progress['synced_codes']}/{progress['total_codes']} ({pct:.1f}%), "
                                   f"新增 {progress['new_records']:,} 条, 跳过 {progress['skip_records']:,} 条, "
                                   f"失败 {progress['failed_records']:,} 条")

                if new_records:
                    try:
                        inserted = ch_client.insert_kline_1min(new_records)
                        if inserted < len(new_records):
                            async with progress_lock:
                                progress["failed_records"] += (len(new_records) - inserted)
                    except Exception as e:
                        logger.error(f"写入 {code} 失败: {e}")
                        async with progress_lock:
                            progress["failed_records"] += len(new_records)


async def sync_market(incremental: bool = False, workers: int = CONCURRENCY):
    """同步全市场数据"""
    # 获取股票列表
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

    # 获取本地最新数据时间（增量同步用）
    code_latest_times = {}
    if incremental:
        logger.info("获取本地数据最新时间...")
        code_latest_times = CHHelper.get_code_latest_times(ch_client)
        logger.info(f"本地已有 {len(code_latest_times)} 只股票的数据")

        # 显示几个示例
        sample_codes = list(code_latest_times.keys())[:3]
        for c in sample_codes:
            logger.info(f"  {c}: {code_latest_times[c].strftime('%Y-%m-%d %H:%M')}")
    else:
        logger.info("全量同步模式：获取所有数据")

    # 进度
    progress = {
        "synced_codes": 0,
        "total_codes": len(codes),
        "synced_records": 0,
        "new_records": 0,
        "skip_records": 0,
        "failed_records": 0,
        "last_code": ""
    }
    progress_lock = asyncio.Lock()
    sem = asyncio.Semaphore(workers)

    # 分片
    chunk_size = max(1, len(codes) // workers)
    chunks = [codes[i:i+chunk_size] for i in range(0, len(codes), chunk_size)]

    logger.info(f"使用 {workers} 个协程并发处理...")

    # 执行
    start_time = time.time()
    tasks = [worker(i, chunk, ch_client, progress, progress_lock, sem, code_latest_times)
             for i, chunk in enumerate(chunks)]
    await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    logger.info(f"同步完成: 共 {len(codes)} 只股票")
    logger.info(f"  新增记录: {progress['new_records']:,} 条")
    logger.info(f"  跳过记录: {progress['skip_records']:,} 条")
    logger.info(f"  失败记录: {progress['failed_records']:,} 条")
    logger.info(f"  耗时: {elapsed:.1f}秒")


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

            count_result = CHHelper.count_code(ch_client, code)
            latest = CHHelper.get_latest_time(ch_client, code)
            logger.info(f"股票 {code} 在库中共有 {count_result} 条，最新时间: {latest}")


async def sync_code_incremental(code: str):
    """增量同步单只股票（测试用）"""
    logger.info(f"增量同步单只股票: {code}")

    ch_client = ClickHouseClient()
    latest = CHHelper.get_latest_time(ch_client, code)
    if latest:
        logger.info(f"本地最新时间: {latest.strftime('%Y-%m-%d %H:%M:%S')}")

    async with aiohttp.ClientSession() as session:
        code, count, records = await fetch_kline(session, code)
        logger.info(f"获取到 {count} 条数据")

        if records:
            # 过滤新数据
            new_records = filter_new_records(records, latest)
            logger.info(f"新增数据: {len(new_records)} 条")

            if new_records:
                inserted = ch_client.insert_kline_1min(new_records)
                logger.info(f"写入 {inserted} 条到ClickHouse")

            count_result = CHHelper.count_code(ch_client, code)
            logger.info(f"股票 {code} 在库中共有 {count_result} 条")


# ============== 主函数 ==============

def main():
    parser = argparse.ArgumentParser(description='TDX 1分钟K线同步工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--full', action='store_true', help='全量同步（获取全部数据）')
    group.add_argument('--incremental', action='store_true', help='增量同步（只获取最新数据）')
    group.add_argument('--code', help='测试用：同步单只股票')
    group.add_argument('--code-incremental', help='增量同步单只股票')

    parser.add_argument('--workers', type=int, default=CONCURRENCY, help=f'并发数 (默认{CONCURRENCY})')

    args = parser.parse_args()

    try:
        if args.code:
            asyncio.run(sync_single(args.code))
        elif args.code_incremental:
            asyncio.run(sync_code_incremental(args.code_incremental))
        elif args.full:
            asyncio.run(sync_market(incremental=False, workers=args.workers))
        elif args.incremental:
            asyncio.run(sync_market(incremental=True, workers=args.workers))
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"同步失败: {e}")


if __name__ == "__main__":
    main()
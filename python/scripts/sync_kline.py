#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX 1分钟K线数据同步脚本
支持按天/按月/按年/全量同步到ClickHouse

Usage:
    python sync_kline.py --date 20241103    # 同步单天
    python sync_kline.py --month 202411     # 同步单月
    python sync_kline.py --year 2024        # 同步单年
    python sync_kline.py --all               # 同步全量
    python sync_kline.py --code 000001       # 测试单只
"""

import sys
import os
import json
import time
import signal
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from functools import wraps

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tdxdata as tdx
from tdxdata.clickhouse import ClickHouseClient
from tdxdata.clickhouse_config import BATCH_SIZE

# ============== 配置 ==============
PROGRESS_FILE = "sync_progress.json"
LOG_FILE = "sync_kline.log"

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

def retry(max_attempts=3, base_delay=2):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), 60)
                    logger.warning(f"{func.__name__} 失败(第{attempt+1}次): {e}, {delay}秒后重试")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def date_range(start: str, end: str) -> List[str]:
    """生成日期范围内的所有日期"""
    start_dt = datetime.strptime(start, "%Y%m%d")
    end_dt = datetime.strptime(end, "%Y%m%d")
    dates = []
    current = start_dt
    while current <= end_dt:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    return dates


def month_end_date(year: str, month: str) -> str:
    """计算月末日期"""
    month, year = int(month), int(year)
    if month == 12:
        return f"{year}1231"
    next_month = datetime(year, month + 1, 1) - timedelta(days=1)
    return next_month.strftime("%Y%m%d")


def get_time_range(period: str, value: str) -> Tuple[str, str]:
    """根据同步周期计算时间范围"""
    today = datetime.now().strftime("%Y%m%d")

    if period == 'day':
        return value, value
    elif period == 'month':
        year, month = value[:4], value[4:]
        start = f"{year}{month}01"
        end = month_end_date(year, month)
        return start, end
    elif period == 'year':
        return f"{value}0101", f"{value}1231"
    elif period == 'all':
        return "19900101", today
    else:
        raise ValueError(f"Unknown period: {period}")


def add_days(date_str: str, days: int) -> str:
    """日期加减天数"""
    dt = datetime.strptime(date_str, "%Y%m%d")
    dt += timedelta(days=days)
    return dt.strftime("%Y%m%d")


def parse_time(ts) -> str:
    """解析时间为ClickHouse格式"""
    if hasattr(ts, 'strftime'):
        try:
            return ts.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    if isinstance(ts, str):
        # ISO格式: 2025-12-01T09:31:00+08:00 或 2025-12-01 09:31:00+08:00
        ts = ts.replace('+08:00', '').replace('T', ' ')
        return ts[:19]
    if hasattr(ts, 'replace'):
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


# ============== 进度管理 ==============

class ProgressManager:
    """进度管理器"""

    def __init__(self, progress_file: str = PROGRESS_FILE):
        self.progress_file = progress_file
        self.progress = {
            "start_time": "",
            "mode": "",
            "target": "",
            "start_date": "",
            "end_date": "",
            "last_code": "",
            "synced_codes": 0,
            "total_codes": 0,
            "synced_records": 0,
            "errors": []
        }
        self._register_signal()

    def _register_signal(self):
        """注册信号处理"""
        signal.signal(signal.SIGINT, self._save_on_interrupt)
        signal.signal(signal.SIGTERM, self._save_on_interrupt)

    def _save_on_interrupt(self, signum, frame):
        """中断时保存进度"""
        logger.info("捕获中断信号，正在保存进度...")
        self.save()
        sys.exit(0)

    def load(self) -> bool:
        """加载进度文件"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    self.progress = json.load(f)
                logger.info(f"从进度文件恢复: last_code={self.progress.get('last_code')}")
                return True
            except Exception as e:
                logger.warning(f"加载进度失败: {e}")
        return False

    def save(self):
        """保存进度到文件"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存进度失败: {e}")

    def add_error(self, code: str, error: str):
        """添加错误记录"""
        self.progress["errors"].append({
            "code": code,
            "error": error,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if len(self.progress["errors"]) > 20:
            self.progress["errors"] = self.progress["errors"][-20:]


# ============== 同步核心 ==============

class KlineSyncer:
    """K线数据同步器"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.ch_client = ClickHouseClient()

        if not self.dry_run:
            if not self.ch_client.test_connection():
                raise ConnectionError("ClickHouse连接失败")
            logger.info("ClickHouse连接成功")

    def get_stock_list(self) -> List[Dict]:
        """获取股票列表"""
        logger.info("获取股票列表...")
        result = tdx.get_stock_list("all")

        if result.get('code') != 0:
            raise Exception(f"获取股票列表失败: {result.get('message')}")

        data = result.get('data', {})
        codes = data.get('codes', [])

        logger.info(f"获取到 {len(codes)} 只股票")
        return codes

    @retry(max_attempts=3, base_delay=2)
    def fetch_kline(self, code: str, period: str = "minute1", limit: int = 800) -> List[Dict]:
        """获取K线数据（带重试）"""
        df = tdx.get_kline(code, period=period, limit=limit)

        if df is None or df.empty:
            return []

        records = []
        exchange = get_exchange(code)

        for _, row in df.iterrows():
            try:
                # 跳过无效数据
                close = row.get('close', 0)
                if close <= 0:
                    continue

                record = {
                    'code': code,
                    'exchange': exchange,
                    'time': parse_time(row.get('time')),
                    'open': int(close * 1000),
                    'high': int(row.get('high', close) * 1000),
                    'low': int(row.get('low', close) * 1000),
                    'close': int(close * 1000),
                    'volume': int(row.get('volume', 0)),
                    'amount': int(row.get('amount', 0) * 1000),
                }
                records.append(record)
            except Exception as e:
                logger.warning(f"处理数据行失败: {e}")
                continue

        return records

    def sync_stock(self, code: str, start_date: str, end_date: str) -> int:
        """同步单只股票的K线数据"""
        try:
            records = self.fetch_kline(code, "minute1", 800)

            if not records:
                logger.debug(f"股票 {code} 无数据")
                return 0

            if self.dry_run:
                logger.info(f"[DRY RUN] 股票 {code} 将写入 {len(records)} 条")
                return len(records)

            inserted = self.ch_client.insert_kline_1min(records)
            logger.debug(f"股票 {code} 写入 {inserted} 条")
            return inserted

        except Exception as e:
            logger.error(f"同步股票 {code} 失败: {e}")
            self.progress.add_error(code, str(e))
            return 0

    def sync_by_period(self, period: str, value: str, resume: bool = False):
        """按周期同步"""
        # 计算时间范围
        start_date, end_date = get_time_range(period, value)
        logger.info(f"同步模式: {period}, 范围: {start_date} ~ {end_date}")

        # 初始化进度
        self.progress.progress["mode"] = period
        self.progress.progress["target"] = value
        self.progress.progress["start_date"] = start_date
        self.progress.progress["end_date"] = end_date
        self.progress.progress["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 加载进度（恢复模式）
        if resume:
            self.progress.load()

        # 获取股票列表
        stock_list = self.get_stock_list()
        self.progress.progress["total_codes"] = len(stock_list)

        # 遍历股票同步
        synced_total = 0
        error_count = 0
        last_code = self.progress.progress.get("last_code", "")

        for i, stock in enumerate(stock_list):
            code = stock.get('code', '')
            if not code:
                continue

            # 恢复模式：跳过已处理的
            if resume and last_code and code != last_code:
                continue
            elif resume and last_code:
                resume = False  # 找到恢复点

            # 更新进度
            self.progress.progress["synced_codes"] = i + 1
            self.progress.progress["last_code"] = code

            # 同步这只股票
            count = self.sync_stock(code, start_date, end_date)
            synced_total += count

            # 每处理10只股票保存进度
            if (i + 1) % 10 == 0:
                self.progress.progress["synced_records"] += synced_total
                self.progress.save()

            # 每处理100只股票输出进度
            if (i + 1) % 100 == 0:
                pct = (i + 1) / len(stock_list) * 100
                logger.info(f"进度: {i+1}/{len(stock_list)} ({pct:.1f}%), 已同步 {synced_total:,} 条")

        # 最终统计
        logger.info(f"同步完成: 共 {len(stock_list)} 只股票, {synced_total:,} 条记录")
        if error_count > 0:
            logger.warning(f"错误数: {error_count}")
        if self.progress.progress["errors"]:
            logger.warning(f"错误列表: {self.progress.progress['errors']}")

    def sync_single(self, code: str):
        """同步单只股票（测试用）"""
        logger.info(f"测试同步单只股票: {code}")
        logger.info(f"交易所: {get_exchange(code)}")

        try:
            records = self.fetch_kline(code, "minute1", 800)
            logger.info(f"获取到 {len(records)} 条数据")

            if records and not self.dry_run:
                inserted = self.ch_client.insert_kline_1min(records)
                logger.info(f"写入 {inserted} 条到ClickHouse")

                # 验证
                count = self.ch_client.get_count(code)
                logger.info(f"股票 {code} 在库中共有 {count} 条")
        except Exception as e:
            logger.error(f"同步失败: {e}")


# ============== 主函数 ==============

def main():
    parser = argparse.ArgumentParser(description='TDX 1分钟K线同步工具')

    # 同步模式
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--date', help='同步指定日期 (YYYYMMDD)')
    group.add_argument('--month', help='同步指定月份 (YYYYMM)')
    group.add_argument('--year', help='同步指定年份 (YYYY)')
    group.add_argument('--all', action='store_true', help='同步全量数据')
    group.add_argument('--code', help='测试用：同步单只股票')

    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际写入')
    parser.add_argument('--resume', action='store_true', help='从上次进度继续')

    args = parser.parse_args()

    try:
        syncer = KlineSyncer(dry_run=args.dry_run)

        if args.code:
            syncer.sync_single(args.code)
        elif args.all:
            syncer.sync_by_period('all', 'all', resume=args.resume)
        elif args.year:
            syncer.sync_by_period('year', args.year, resume=args.resume)
        elif args.month:
            syncer.sync_by_period('month', args.month, resume=args.resume)
        elif args.date:
            syncer.sync_by_period('day', args.date, resume=args.resume)

    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"同步失败: {e}")


if __name__ == "__main__":
    main()
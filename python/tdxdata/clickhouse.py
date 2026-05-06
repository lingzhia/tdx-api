# -*- coding: utf-8 -*-
"""
ClickHouse客户端封装
用于tdxdata 1分钟K线数据入库
使用HTTP接口避免时区问题
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests

from .clickhouse_config import (
    CH_HOST, CH_PORT, CH_USER, CH_PASSWORD, CH_DATABASE,
    CH_TABLE_KLINE_1MIN, BATCH_SIZE
)


class ClickHouseClient:
    """ClickHouse客户端封装（HTTP接口）"""

    def __init__(self,
                 host: str = CH_HOST,
                 port: int = 8123,  # HTTP端口
                 user: str = CH_USER,
                 password: str = CH_PASSWORD,
                 database: str = CH_DATABASE):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._base_url = f"http://{host}:{port}"

    def _execute(self, query: str) -> Optional:
        """执行SQL查询"""
        try:
            response = requests.post(
                self._base_url,
                data=query.encode('utf-8'),
                auth=(self.user, self.password),
                headers={'Content-Type': 'text/plain'},
                timeout=60
            )
            if response.status_code != 200:
                raise Exception(f"Query failed: {response.text}")
            return response.text
        except Exception as e:
            print(f"执行失败: {e}")
            return None

    def test_connection(self) -> bool:
        """测试连接"""
        try:
            result = self._execute("SELECT 1")
            return result is not None
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def insert_kline_1min(self, data: List[Dict]) -> int:
        """
        批量插入1分钟K线数据

        Args:
            data: K线数据列表，每条包含:
                code, exchange, time, open, high, low, close, volume, amount

        Returns:
            插入条数
        """
        if not data:
            return 0

        # 分批插入，避免URL过长
        BATCH = 5000
        RETRY = 3
        total = len(data)
        inserted = 0

        for i in range(0, total, BATCH):
            batch = data[i:i+BATCH]
            batch_query = (
                f"INSERT INTO {CH_DATABASE}.{CH_TABLE_KLINE_1MIN} "
                f"(code, exchange, time, open, high, low, close, volume, amount) VALUES "
                + ','.join([
                    f"('{item.get('code', '')}', '{item.get('exchange', '')}', '{item.get('time', '')}', "
                    f"{int(item.get('open', 0))}, {int(item.get('high', 0))}, {int(item.get('low', 0))}, "
                    f"{int(item.get('close', 0))}, {int(item.get('volume', 0))}, {int(item.get('amount', 0))})"
                    for item in batch
                ])
            )

            # 重试机制
            for retry in range(RETRY):
                result = self._execute(batch_query)
                if result is not None:
                    inserted += len(batch)
                    break
                elif retry < RETRY - 1:
                    import time
                    time.sleep(0.5 * (retry + 1))  # 递增延迟
            else:
                print(f"Batch {i//BATCH} insert failed after {RETRY} retries")

        return inserted

    def get_count(self, code: str = None) -> int:
        """
        获取记录数

        Args:
            code: 股票代码，不传则返回总数

        Returns:
            记录数
        """
        if code:
            sql = f"SELECT count() FROM {CH_DATABASE}.{CH_TABLE_KLINE_1MIN} WHERE code = '{code}'"
        else:
            sql = f"SELECT count() FROM {CH_DATABASE}.{CH_TABLE_KLINE_1MIN}"

        result = self._execute(sql)
        if result is None:
            return 0

        try:
            return int(result.strip())
        except:
            return 0

    def get_latest_time(self, code: str) -> Optional[datetime]:
        """
        获取某股票最新数据时间

        Args:
            code: 股票代码

        Returns:
            最新时间或None
        """
        sql = f"SELECT max(time) FROM {CH_DATABASE}.{CH_TABLE_KLINE_1MIN} WHERE code = '{code}'"
        result = self._execute(sql)
        if result is None or result.strip() == '' or result.strip() == '0':
            return None

        try:
            return datetime.fromisoformat(result.strip().replace('+08:00', ''))
        except:
            return None

    def get_sync_progress(self) -> Dict:
        """
        获取同步进度

        Returns:
            包含总股票数、已同步数、记录总数
        """
        # 获取已同步的股票数
        sql = f"SELECT count(DISTINCT code) FROM {CH_DATABASE}.{CH_TABLE_KLINE_1MIN}"
        result = self._execute(sql)
        synced_count = int(result.strip()) if result else 0

        # 获取总记录数
        total_records = self.get_count()

        return {
            'synced_count': synced_count,
            'total_records': total_records
        }

    def table_exists(self, table: str) -> bool:
        """检查表是否存在"""
        sql = f"EXISTS TABLE {table}"
        result = self._execute(sql)
        return result.strip() == '1' if result else False

    def drop_table(self, table: str):
        """删除表"""
        self._execute(f"DROP TABLE IF EXISTS {table}")
        print(f"表 {table} 已删除")


# 全局客户端实例
_client: Optional[ClickHouseClient] = None


def get_client() -> ClickHouseClient:
    """获取全局ClickHouse客户端"""
    global _client
    if _client is None:
        _client = ClickHouseClient()
    return _client
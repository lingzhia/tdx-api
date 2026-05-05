# -*- coding: utf-8 -*-
"""
tdxdata 测试用例
"""

import sys
import os

# 添加包路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tdxdata as tdx
from tdxdata import TDXError, TDXConnectionError, TDXAPIError


def test_health():
    """测试健康检查"""
    print("\n=== 测试 health ===")
    result = tdx.health()
    print(f"health: {result}")
    assert result is not None
    assert 'status' in result.get('data', {}) or 'status' in result


def test_get_quote():
    """测试获取五档行情"""
    print("\n=== 测试 get_quote ===")
    df = tdx.get_quote("000001")
    print(f"quote类型: {type(df)}")
    print(f"quote列: {df.columns.tolist()}")
    print(f"quote数据:\n{df.head()}")
    assert not df.empty
    assert 'code' in df.columns
    assert 'close' in df.columns
    # 验证价格转换（应该是元，不是厘）
    assert df['close'].iloc[0] < 1000, "价格应该是元，不应该是厘"


def test_get_quote_multiple():
    """测试获取多个股票行情"""
    print("\n=== 测试 get_quote (多股票) ===")
    df = tdx.get_quote("000001,600519")
    print(f"多股票行情数量: {len(df)}")
    print(f"数据:\n{df[['code', 'close']]}")
    assert len(df) >= 2


def test_get_kline():
    """测试获取K线"""
    print("\n=== 测试 get_kline ===")
    df = tdx.get_kline("000001", period="day", limit=5)
    print(f"kline类型: {type(df)}")
    print(f"kline列: {df.columns.tolist()}")
    print(f"kline数据:\n{df}")
    assert not df.empty
    assert 'time' in df.columns
    assert 'close' in df.columns
    # 验证价格转换
    assert df['close'].iloc[0] < 1000


def test_get_kline_minute():
    """测试获取分钟K线"""
    print("\n=== 测试 get_kline (分钟) ===")
    df = tdx.get_kline("000001", period="minute5", limit=10)
    print(f"分钟K线数量: {len(df)}")
    print(f"数据:\n{df}")


def test_get_minute():
    """测试获取分时数据"""
    print("\n=== 测试 get_minute ===")
    df = tdx.get_minute("000001")
    print(f"minute类型: {type(df)}")
    print(f"minute列: {df.columns.tolist()}")
    print(f"minute数据:\n{df.head()}")


def test_get_trade():
    """测试获取逐笔成交"""
    print("\n=== 测试 get_trade ===")
    df = tdx.get_trade("000001")
    print(f"trade类型: {type(df)}")
    print(f"trade列: {df.columns.tolist()}")
    print(f"trade数据:\n{df.head()}")


def test_search_stock():
    """测试搜索股票"""
    print("\n=== 测试 search_stock ===")
    df = tdx.search_stock("茅台")
    print(f"search结果:\n{df}")
    assert not df.empty
    assert 'code' in df.columns
    assert 'name' in df.columns


def test_search_stock_by_code():
    """测试按代码搜索"""
    print("\n=== 测试 search_stock (按代码) ===")
    df = tdx.search_stock("000001")
    print(f"搜索000001结果:\n{df}")


def test_get_stock_info():
    """测试获取股票综合信息"""
    print("\n=== 测试 get_stock_info ===")
    info = tdx.get_stock_info("000001")
    print(f"stock_info类型: {type(info)}")
    print(f"stock_info keys: {info.keys() if isinstance(info, dict) else 'N/A'}")


def test_batch_quote():
    """测试批量获取行情"""
    print("\n=== 测试 batch_quote ===")
    result = tdx.batch_quote(["000001", "600519"])
    print(f"batch_quote类型: {type(result)}")
    print(f"batch_quote结果数量: {len(result) if isinstance(result, list) else 'N/A'}")


def test_get_stock_list():
    """测试获取股票列表"""
    print("\n=== 测试 get_stock_list ===")
    result = tdx.get_stock_list("sh")
    print(f"stock_list类型: {type(result)}")
    print(f"stock_list keys: {result.keys() if isinstance(result, dict) else 'N/A'}")


def test_get_etf_list():
    """测试获取ETF列表"""
    print("\n=== 测试 get_etf_list ===")
    result = tdx.get_etf_list(exchange="sh", limit=5)
    print(f"etf_list类型: {type(result)}")
    print(f"etf_list: {result}")


def test_get_workday_info():
    """测试获取交易日信息"""
    print("\n=== 测试 get_workday_info ===")
    result = tdx.get_workday_info("20241103")
    print(f"workday_info: {result}")


def test_is_workday():
    """测试判断是否交易日"""
    print("\n=== 测试 is_workday ===")
    is_workday = tdx.is_workday("20241103")
    print(f"20241103是否交易日: {is_workday}")
    assert isinstance(is_workday, bool)


def test_get_next_workday():
    """测试获取下一个交易日"""
    print("\n=== 测试 get_next_workday ===")
    next_days = tdx.get_next_workday("20241103", count=3)
    print(f"下一个交易日: {next_days}")


def test_get_market_count():
    """测试获取市场证券数量"""
    print("\n=== 测试 get_market_count ===")
    result = tdx.get_market_count()
    print(f"market_count: {result}")


def test_get_index():
    """测试获取指数K线"""
    print("\n=== 测试 get_index ===")
    df = tdx.get_index("sh000001", period="day")
    print(f"index类型: {type(df)}")
    print(f"index列: {df.columns.tolist()}")
    print(f"index数据:\n{df.head()}")


def test_get_income():
    """测试收益区间"""
    print("\n=== 测试 get_income ===")
    result = tdx.get_income("000001", "20240101", days="5,10,20")
    print(f"income: {result}")


def test_get_server_status():
    """测试获取服务状态"""
    print("\n=== 测试 get_server_status ===")
    result = tdx.get_server_status()
    print(f"server_status: {result}")


def test_exceptions():
    """测试异常处理"""
    print("\n=== 测试异常处理 ===")
    # 测试连接异常
    try:
        # 使用一个无效的代码测试
        tdx.get_quote("")
    except TDXAPIError as e:
        print(f"捕获到API异常: code={e.code}, message={e.message}")
    except TDXError as e:
        print(f"捕获到TDX异常: {e}")
    except Exception as e:
        print(f"捕获到其他异常: {type(e).__name__}: {e}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("tdxdata 测试开始")
    print("=" * 50)

    tests = [
        test_health,
        test_get_quote,
        test_get_quote_multiple,
        test_get_kline,
        test_get_kline_minute,
        test_get_minute,
        test_get_trade,
        test_search_stock,
        test_search_stock_by_code,
        test_get_stock_info,
        test_batch_quote,
        test_get_stock_list,
        test_get_etf_list,
        test_get_workday_info,
        test_is_workday,
        test_get_next_workday,
        test_get_market_count,
        test_get_index,
        test_get_income,
        test_get_server_status,
        test_exceptions,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n!!! 测试失败: {test.__name__}")
            print(f"    错误: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"测试完成: 通过={passed}, 失败={failed}")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()

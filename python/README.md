# tdxdata

> 通达信股票数据Python包，类jqdata风格

## 特性

- **类jqdata风格**：直接函数调用，无需实例化客户端
- **覆盖全部接口**：32个API接口完整封装
- **返回DataFrame**：主要数据接口返回pandas.DataFrame
- **零配置使用**：连接信息已写死，开箱即用
- **类型提示完整**：支持IDE自动补全

## 安装

```bash
# 开发模式安装
cd python
pip install -e .

# 或者直接安装
pip install requests pandas
```

## 快速开始

```python
import tdxdata as tdx

# 初始化（可选，懒加载会自动调用）
tdx.auth()

# ========== 行情数据 ==========

# 获取五档行情
df = tdx.get_quote("000001")

# 获取K线
df = tdx.get_kline("000001", period="day", limit=100)

# 获取分时数据
df = tdx.get_minute("000001")

# 获取逐笔成交
df = tdx.get_trade("000001")

# 搜索股票
df = tdx.search_stock("茅台")

# 获取股票综合信息
info = tdx.get_stock_info("000001")
```

## API列表

### 行情数据

| 函数 | 说明 |
|------|------|
| `get_quote(code)` | 获取五档行情，支持逗号分隔多代码 |
| `get_kline(code, period, limit)` | 获取K线数据 |
| `get_minute(code, date)` | 获取分时数据 |
| `get_trade(code, date)` | 获取逐笔成交 |
| `search_stock(keyword)` | 搜索股票 |
| `get_stock_info(code)` | 获取股票综合信息 |

### 批量接口

| 函数 | 说明 |
|------|------|
| `batch_quote(codes)` | 批量获取行情 |
| `get_stock_list(exchange)` | 获取股票列表 |

### K线扩展

| 函数 | 说明 |
|------|------|
| `get_kline_history(code, period, start_date, end_date, limit)` | 获取指定时间范围K线 |
| `get_kline_all(code, period, limit)` | 获取全量历史K线 |
| `get_kline_all_tdx(code, period, limit)` | 获取通达信原始K线 |
| `get_kline_all_ths(code, period, limit)` | 获取同花顺前复权K线 |

### 指数

| 函数 | 说明 |
|------|------|
| `get_index(code, period)` | 获取指数K线 |
| `get_index_all(code, period, limit)` | 获取指数全量K线 |

### 分时成交

| 函数 | 说明 |
|------|------|
| `get_trade_history(code, date, start, count)` | 历史分时成交(分页) |
| `get_minute_trade_all(code, date)` | 全天分时成交 |
| `get_trade_history_full(code, before, limit)` | 上市以来全部分时成交 |

### ETF

| 函数 | 说明 |
|------|------|
| `get_etf_list(exchange, limit)` | 获取ETF列表 |
| `get_etf_codes(limit, prefix)` | 获取ETF代码列表 |

### 股票代码

| 函数 | 说明 |
|------|------|
| `get_stock_codes(limit, prefix)` | 获取股票代码列表 |

### 交易日

| 函数 | 说明 |
|------|------|
| `get_workday_info(date, count)` | 查询交易日信息 |
| `get_workday_range(start, end)` | 获取交易日范围 |
| `is_workday(date)` | 判断是否交易日 |
| `get_next_workday(date, count)` | 获取下一个交易日 |
| `get_previous_workday(date, count)` | 获取上一个交易日 |

### 市场数据

| 函数 | 说明 |
|------|------|
| `get_market_count()` | 获取市场证券数量 |
| `get_market_stats()` | 获取市场统计 |

### 收益分析

| 函数 | 说明 |
|------|------|
| `get_income(code, start_date, days)` | 计算收益区间 |

### 任务管理

| 函数 | 说明 |
|------|------|
| `create_kline_task(codes, tables, limit, start_date)` | 创建K线入库任务 |
| `create_trade_task(code, start_year, end_year)` | 创建分时成交入库任务 |
| `list_tasks()` | 获取任务列表 |
| `get_task(task_id)` | 获取任务详情 |
| `cancel_task(task_id)` | 取消任务 |

### 系统

| 函数 | 说明 |
|------|------|
| `health()` | 健康检查 |
| `get_server_status()` | 获取服务状态 |

## K线周期

| period | 说明 |
|--------|------|
| `minute1` | 1分钟K线 |
| `minute5` | 5分钟K线 |
| `minute15` | 15分钟K线 |
| `minute30` | 30分钟K线 |
| `hour` | 60分钟K线 |
| `day` | 日K线 |
| `week` | 周K线 |
| `month` | 月K线 |

## 数据说明

- **价格单位**：返回元（API原返回厘，已自动转换）
- **成交量单位**：手
- **日期格式**：YYYYMMDD 或 YYYY-MM-DD

## 返回类型

| 函数 | 返回类型 |
|------|----------|
| `get_quote()` | pandas.DataFrame |
| `get_kline()` | pandas.DataFrame |
| `get_minute()` | pandas.DataFrame |
| `get_trade()` | pandas.DataFrame |
| `search_stock()` | pandas.DataFrame |
| `get_stock_info()` | dict |
| 其他 | dict 或 list |

## 异常处理

```python
import tdxdata as tdx
from tdxdata import TDXError, TDXConnectionError, TDXAPIError

try:
    df = tdx.get_quote("000001")
except TDXConnectionError as e:
    print(f"连接失败: {e}")
except TDXAPIError as e:
    print(f"API错误: {e.code} {e.message}")
except TDXError as e:
    print(f"其他错误: {e}")
```

## 使用示例

### 选股策略：多头排列

```python
import tdxdata as tdx
import pandas as pd

def screen_multihead(codes):
    """筛选多头排列股票（MA5>MA10>MA20）"""
    selected = []
    for code in codes:
        df = tdx.get_kline(code, period="day", limit=20)
        if len(df) >= 20:
            ma5 = df['close'][:5].mean()
            ma10 = df['close'][:10].mean()
            ma20 = df['close'][:20].mean()
            if ma5 > ma10 > ma20:
                selected.append({
                    'code': code,
                    'price': df['close'].iloc[0],
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20
                })
    return pd.DataFrame(selected)

# 使用
candidates = screen_multihead(['000001', '600519', '601318'])
print(candidates)
```

### 实时监控

```python
import tdxdata as tdx

def monitor_stocks(codes):
    """监控股票实时涨跌"""
    quotes = tdx.batch_quote(codes)
    for q in quotes:
        code = q['Code']
        last = q['K']['Last'] / 1000  # 昨收
        close = q['K']['Close'] / 1000  # 今收
        pct = (close - last) / last * 100
        print(f"{code}: {close:.2f} ({pct:+.2f}%)")

monitor_stocks(['000001', '600519', '601318'])
```

## 配置

连接信息已写死在内置配置中：

```python
DEFAULT_HOST = "100.107.142.74"
DEFAULT_PORT = 8080
```

如需修改，编辑 `tdxdata/config.py`

## License

MIT

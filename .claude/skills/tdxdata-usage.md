---
name: tdxdata-usage
description: tdxdata量化数据Python包使用指南，当用户需要获取A股市场数据、股票行情、K线数据时使用此skill。tdxdata封装了tdx-api的32个RESTful接口，提供类jqdata风格的函数式接口。
triggers:
  - 获取A股数据
  - 股票行情
  - K线数据
  - 分时数据
  - 量化数据
  - tdxdata
  - get_quote
  - get_kline
  - search_stock
---

# tdxdata 使用指南

## 概述

tdxdata 是一个类jqdata风格的A股数据Python包，封装了tdx-api的全部32个RESTful接口，提供实时行情、K线数据、分时数据等功能。

**服务地址**: `http://100.107.142.74:8080`

---

## 快速开始

```python
import tdxdata as tdx

# 初始化（可选，懒加载会自动调用）
tdx.auth()

# 获取五档行情
df = tdx.get_quote("000001")

# 获取K线
df = tdx.get_kline("000001", period="day", limit=100)

# 搜索股票
df = tdx.search_stock("茅台")
```

---

## 核心API

### 行情数据

| 函数 | 说明 |
|------|------|
| `tdx.get_quote(code)` | 获取五档行情，支持逗号分隔多代码 |
| `tdx.get_kline(code, period, limit)` | 获取K线数据 |
| `tdx.get_minute(code, date)` | 获取分时数据 |
| `tdx.get_trade(code, date)` | 获取逐笔成交 |
| `tdx.search_stock(keyword)` | 搜索股票 |
| `tdx.get_stock_info(code)` | 获取股票综合信息 |

### 批量接口

| 函数 | 说明 |
|------|------|
| `tdx.batch_quote(codes)` | 批量获取行情 |
| `tdx.get_stock_list(exchange)` | 获取股票列表 |

### K线扩展

| 函数 | 说明 |
|------|------|
| `tdx.get_kline_history(code, period, start_date, end_date, limit)` | 获取指定时间范围K线 |
| `tdx.get_kline_all(code, period, limit)` | 获取全量历史K线 |
| `tdx.get_kline_all_tdx(code, period, limit)` | 获取通达信原始K线 |
| `tdx.get_kline_all_ths(code, period, limit)` | 获取同花顺前复权K线 |

### 指数

| 函数 | 说明 |
|------|------|
| `tdx.get_index(code, period)` | 获取指数K线 |
| `tdx.get_index_all(code, period, limit)` | 获取指数全量K线 |

### 分时成交

| 函数 | 说明 |
|------|------|
| `tdx.get_trade_history(code, date, start, count)` | 历史分时成交(分页) |
| `tdx.get_minute_trade_all(code, date)` | 全天分时成交 |
| `tdx.get_trade_history_full(code, before, limit)` | 上市以来全部分时成交 |

### ETF

| 函数 | 说明 |
|------|------|
| `tdx.get_etf_list(exchange, limit)` | 获取ETF列表 |
| `tdx.get_etf_codes(limit, prefix)` | 获取ETF代码列表 |

### 股票代码

| 函数 | 说明 |
|------|------|
| `tdx.get_stock_codes(limit, prefix)` | 获取股票代码列表 |

### 交易日

| 函数 | 说明 |
|------|------|
| `tdx.get_workday_info(date, count)` | 查询交易日信息 |
| `tdx.get_workday_range(start, end)` | 获取交易日范围 |
| `tdx.is_workday(date)` | 判断是否交易日 |
| `tdx.get_next_workday(date, count)` | 获取下一个交易日 |
| `tdx.get_previous_workday(date, count)` | 获取上一个交易日 |

### 市场数据

| 函数 | 说明 |
|------|------|
| `tdx.get_market_count()` | 获取市场证券数量 |
| `tdx.get_market_stats()` | 获取市场统计 |

### 收益分析

| 函数 | 说明 |
|------|------|
| `tdx.get_income(code, start_date, days)` | 计算收益区间 |

### 任务管理

| 函数 | 说明 |
|------|------|
| `tdx.create_kline_task(codes, tables, limit, start_date)` | 创建K线入库任务 |
| `tdx.create_trade_task(code, start_year, end_year)` | 创建分时成交入库任务 |
| `tdx.list_tasks()` | 获取任务列表 |
| `tdx.get_task(task_id)` | 获取任务详情 |
| `tdx.cancel_task(task_id)` | 取消任务 |

### 系统

| 函数 | 说明 |
|------|------|
| `tdx.health()` | 健康检查 |
| `tdx.get_server_status()` | 获取服务状态 |

---

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

---

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

---

## DataFrame列说明

### get_quote 返回列

| 列名 | 说明 |
|------|------|
| code | 股票代码 |
| exchange | 交易所 |
| last | 昨收价(元) |
| open | 开盘价(元) |
| high | 最高价(元) |
| low | 最低价(元) |
| close | 最新价(元) |
| volume | 成交量(手) |
| amount | 成交额(元) |
| buy1~buy5 | 买一~买五价(元) |
| buy1_vol~buy5_vol | 买一~买五量(手) |
| sell1~sell5 | 卖一~卖五价(元) |
| sell1_vol~sell5_vol | 卖一~卖五量(手) |

### get_kline 返回列

| 列名 | 说明 |
|------|------|
| time | 时间 |
| open | 开盘价(元) |
| high | 最高价(元) |
| low | 最低价(元) |
| close | 收盘价(元) |
| volume | 成交量(手) |
| amount | 成交额(元) |

### get_minute 返回列

| 列名 | 说明 |
|------|------|
| time | 时间(HH:MM) |
| price | 价格(元) |
| volume | 成交量(手) |

### get_trade 返回列

| 列名 | 说明 |
|------|------|
| time | 时间 |
| price | 成交价(元) |
| volume | 成交量(手) |
| status | 0=买入,1=卖出,2=中性 |
| number | 成交单数 |

### search_stock 返回列

| 列名 | 说明 |
|------|------|
| code | 股票代码 |
| name | 股票名称 |
| exchange | 交易所 |

---

## 常用指数代码

| code | 说明 |
|------|------|
| sh000001 | 上证指数 |
| sz399001 | 深证成指 |
| sz399006 | 创业板指 |
| sh000300 | 沪深300 |

---

## 使用示例

### 示例1: 获取股票行情并计算涨跌

```python
import tdxdata as tdx

df = tdx.get_quote("000001")
last = df['last'].iloc[0]  # 昨收
close = df['close'].iloc[0]  # 今收
pct = (close - last) / last * 100
print(f"涨跌: {pct:+.2f}%")
```

### 示例2: 获取K线并计算MA

```python
import tdxdata as tdx

df = tdx.get_kline("000001", period="day", limit=20)
ma5 = df['close'][:5].mean()
ma10 = df['close'][:10].mean()
ma20 = df['close'][:20].mean()
print(f"MA5={ma5:.2f}, MA10={ma10:.2f}, MA20={ma20:.2f}")
```

### 示例3: 多头排列选股

```python
import tdxdata as tdx

def screen_multihead(codes):
    selected = []
    for code in codes:
        df = tdx.get_kline(code, period="day", limit=20)
        if len(df) >= 20:
            ma5 = df['close'][:5].mean()
            ma10 = df['close'][:10].mean()
            ma20 = df['close'][:20].mean()
            if ma5 > ma10 > ma20:
                selected.append(code)
    return selected

candidates = screen_multihead(['000001', '600519', '601318'])
print(f"多头排列股票: {candidates}")
```

### 示例4: 实时监控多只股票

```python
import tdxdata as tdx

quotes = tdx.batch_quote(["000001", "600519", "601318"])
for q in quotes:
    code = q['Code']
    close = q['K']['Close'] / 1000
    last = q['K']['Last'] / 1000
    pct = (close - last) / last * 100
    print(f"{code}: {close:.2f} ({pct:+.2f}%)")
```

### 示例5: 搜索并获取数据

```python
import tdxdata as tdx

# 搜索股票
df = tdx.search_stock("茅台")
print(df)

# 获取K线
if not df.empty:
    code = df['code'].iloc[0]
    kline = tdx.get_kline(code, period="day", limit=10)
    print(kline)
```

### 示例6: 指数数据分析

```python
import tdxdata as tdx

# 上证指数日K
df = tdx.get_index("sh000001", period="day", limit=30)
print(df.tail())

# 计算涨跌幅
df['pct_change'] = df['close'].pct_change() * 100
print(f"近30日涨幅: {df['pct_change'].sum():.2f}%")
```

### 示例7: 判断交易日

```python
import tdxdata as tdx

# 判断今天是否交易日
if tdx.is_workday():
    print("今天是交易日")

# 获取下一个交易日
next_day = tdx.get_next_workday(count=1)
print(f"下一个交易日: {next_day}")
```

---

## 异常处理

```python
import tdxdata as tdx
from tdxdata import TDXError, TDXConnectionError, TDXAPIError

try:
    df = tdx.get_quote("000001")
except TDXConnectionError as e:
    print(f"连接失败: {e}")
except TDXAPIError as e:
    print(f"API错误: code={e.code}, message={e.message}")
except TDXError as e:
    print(f"其他错误: {e}")
```

---

## 数据单位

| 数据类型 | API返回 | Python包返回 |
|----------|---------|--------------|
| 价格 | 厘 | 元 (÷1000) |
| 成交量 | 手 | 手 |
| 成交额 | 厘 | 元 (÷1000) |

---

## 注意事项

1. **价格转换**: 所有价格已自动从"厘"转换为"元"
2. **懒加载**: 无需手动调用`auth()`，首次调用API时会自动初始化
3. **非交易时间**: 分时数据在非交易时间可能为空
4. **批量请求**: 建议使用`batch_quote()`批量获取多只股票行情，减少网络请求

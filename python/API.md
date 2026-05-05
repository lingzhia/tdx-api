# tdxdata API 文档

## 概述

tdxdata 封装了tdx-api的全部32个RESTful接口，提供类jqdata风格的Python接口。

**基础URL**: `http://100.107.142.74:8080`

---

## 初始化

### auth()

初始化连接，类似jqdata.auth()

```python
import tdxdata as tdx

tdx.auth()
```

**返回值**: Client实例

**说明**: 懒加载，首次调用API时会自动初始化，可手动调用加速

---

## 行情数据

### get_quote(code)

获取五档行情，支持逗号分隔多代码

```python
df = tdx.get_quote("000001")
df = tdx.get_quote("000001,600519")
```

**参数**:
- `code` (str): 股票代码，支持逗号分隔

**返回值**: DataFrame

**DataFrame列**:
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

---

### get_kline(code, period="day", limit=100)

获取K线数据

```python
df = tdx.get_kline("000001", period="day", limit=100)
df = tdx.get_kline("000001", period="minute15", limit=200)
```

**参数**:
- `code` (str): 股票代码
- `period` (str): K线周期，默认"day"
- `limit` (int): 返回条数，默认100

**period可选值**:
| 值 | 说明 |
|------|------|
| minute1 | 1分钟K线 |
| minute5 | 5分钟K线 |
| minute15 | 15分钟K线 |
| minute30 | 30分钟K线 |
| hour | 60分钟K线 |
| day | 日K线 |
| week | 周K线 |
| month | 月K线 |

**返回值**: DataFrame

**DataFrame列**:
| 列名 | 说明 |
|------|------|
| time | 时间 |
| open | 开盘价(元) |
| high | 最高价(元) |
| low | 最低价(元) |
| close | 收盘价(元) |
| volume | 成交量(手) |
| amount | 成交额(元) |

---

### get_minute(code, date=None)

获取分时数据

```python
df = tdx.get_minute("000001")
df = tdx.get_minute("000001", "20241103")
```

**参数**:
- `code` (str): 股票代码
- `date` (str): 日期YYYYMMDD格式，默认当天

**返回值**: DataFrame

**DataFrame列**:
| 列名 | 说明 |
|------|------|
| time | 时间(HH:MM) |
| price | 价格(元) |
| volume | 成交量(手) |

---

### get_trade(code, date=None)

获取逐笔成交

```python
df = tdx.get_trade("000001")
df = tdx.get_trade("000001", "20241103")
```

**参数**:
- `code` (str): 股票代码
- `date` (str): 日期YYYYMMDD格式，默认当天

**返回值**: DataFrame

**DataFrame列**:
| 列名 | 说明 |
|------|------|
| time | 时间 |
| price | 成交价(元) |
| volume | 成交量(手) |
| status | 0=买入,1=卖出,2=中性 |
| number | 成交单数 |

---

### search_stock(keyword)

搜索股票

```python
df = tdx.search_stock("茅台")
df = tdx.search_stock("000001")
```

**参数**:
- `keyword` (str): 关键词（代码或名称）

**返回值**: DataFrame

**DataFrame列**:
| 列名 | 说明 |
|------|------|
| code | 股票代码 |
| name | 股票名称 |
| exchange | 交易所 |

---

### get_stock_info(code)

获取股票综合信息

```python
info = tdx.get_stock_info("000001")
```

**参数**:
- `code` (str): 股票代码

**返回值**: dict

**dict结构**:
```python
{
    "quote": {...},      # 五档行情
    "kline_day": {...}, # 日K线
    "minute": {...}      # 分时数据
}
```

---

## 批量接口

### batch_quote(codes)

批量获取行情

```python
result = tdx.batch_quote(["000001", "600519", "601318"])
```

**参数**:
- `codes` (list): 股票代码列表

**返回值**: dict

---

### get_stock_list(exchange="all")

获取股票列表

```python
result = tdx.get_stock_list("sh")
result = tdx.get_stock_list("all")
```

**参数**:
- `exchange` (str): 交易所 sh/sz/bj/all，默认all

**返回值**: dict

---

## K线扩展

### get_kline_history(code, period="day", start_date=None, end_date=None, limit=100)

获取指定时间范围K线

```python
df = tdx.get_kline_history("000001", period="day",
                            start_date="20240101",
                            end_date="20241103",
                            limit=100)
```

**参数**:
- `code` (str): 股票代码
- `period` (str): K线周期
- `start_date` (str): 开始日期YYYYMMDD
- `end_date` (str): 结束日期YYYYMMDD
- `limit` (int): 返回条数，默认100

**返回值**: DataFrame

---

### get_kline_all(code, period="day", limit=None)

获取全量历史K线

```python
result = tdx.get_kline_all("000001", period="day")
```

**参数**:
- `code` (str): 股票代码
- `period` (str): K线周期
- `limit` (int): 返回条数限制

**返回值**: dict

---

### get_kline_all_tdx(code, period="day", limit=None)

获取通达信原始K线

```python
result = tdx.get_kline_all_tdx("000001", period="day")
```

**返回值**: dict

---

### get_kline_all_ths(code, period="day", limit=None)

获取同花顺前复权K线

```python
result = tdx.get_kline_all_ths("000001", period="day")
```

**返回值**: dict

---

## 指数

### get_index(code, period="day")

获取指数K线

```python
df = tdx.get_index("sh000001", period="day")
```

**参数**:
- `code` (str): 指数代码，如sh000001
- `period` (str): K线周期

**返回值**: DataFrame

**常用指数代码**:
| code | 说明 |
|------|------|
| sh000001 | 上证指数 |
| sz399001 | 深证成指 |
| sz399006 | 创业板指 |
| sh000300 | 沪深300 |

---

### get_index_all(code, period="day", limit=None)

获取指数全量K线

```python
result = tdx.get_index_all("sh000001", period="day")
```

**返回值**: dict

---

## 分时成交

### get_trade_history(code, date, start=0, count=2000)

历史分时成交(分页)

```python
result = tdx.get_trade_history("000001", "20241103", start=0, count=2000)
```

**返回值**: dict

---

### get_minute_trade_all(code, date=None)

全天分时成交

```python
result = tdx.get_minute_trade_all("000001")
result = tdx.get_minute_trade_all("000001", "20241103")
```

**返回值**: dict

---

### get_trade_history_full(code, before=None, limit=None)

上市以来全部分时成交

```python
result = tdx.get_trade_history_full("000001")
```

**返回值**: dict

---

## ETF

### get_etf_list(exchange=None, limit=None)

获取ETF列表

```python
result = tdx.get_etf_list(exchange="sh", limit=10)
```

**返回值**: dict

---

### get_etf_codes(limit=None, prefix=True)

获取ETF代码列表

```python
result = tdx.get_etf_codes(limit=10)
```

**返回值**: dict

---

## 股票代码

### get_stock_codes(limit=None, prefix=True)

获取股票代码列表

```python
result = tdx.get_stock_codes(limit=10)
```

**返回值**: dict

---

## 交易日

### get_workday_info(date=None, count=1)

查询交易日信息

```python
result = tdx.get_workday_info("20241103", count=1)
```

**返回值**: dict

---

### get_workday_range(start, end)

获取交易日范围

```python
result = tdx.get_workday_range("20241101", "20241108")
```

**返回值**: dict

---

### is_workday(date=None)

判断是否交易日

```python
is_today = tdx.is_workday()
is_work = tdx.is_workday("20241103")
```

**返回值**: bool

---

### get_next_workday(date=None, count=1)

获取下一个交易日

```python
next_days = tdx.get_next_workday(count=3)
```

**返回值**: list

---

### get_previous_workday(date=None, count=1)

获取上一个交易日

```python
prev_days = tdx.get_previous_workday(count=3)
```

**返回值**: list

---

## 市场数据

### get_market_count()

获取市场证券数量

```python
result = tdx.get_market_count()
```

**返回值**: dict

---

### get_market_stats()

获取市场统计

```python
result = tdx.get_market_stats()
```

**返回值**: dict

---

## 收益分析

### get_income(code, start_date, days="5,10,20,60,120")

计算收益区间

```python
result = tdx.get_income("000001", "20240101", days="5,10,20")
```

**返回值**: dict

---

## 任务管理

### create_kline_task(codes=None, tables=None, limit=1, start_date=None)

创建K线入库任务

```python
task_id = tdx.create_kline_task(
    codes=["000001", "600519"],
    tables=["day", "week"],
    limit=4,
    start_date="2020-01-01"
)
```

**返回值**: str (任务ID)

---

### create_trade_task(code, start_year=2000, end_year=None)

创建分时成交入库任务

```python
task_id = tdx.create_trade_task("000001", start_year=2015, end_year=2023)
```

**返回值**: str (任务ID)

---

### list_tasks()

获取任务列表

```python
tasks = tdx.list_tasks()
```

**返回值**: list

---

### get_task(task_id)

获取任务详情

```python
detail = tdx.get_task("task_id_here")
```

**返回值**: dict

---

### cancel_task(task_id)

取消任务

```python
result = tdx.cancel_task("task_id_here")
```

**返回值**: dict

---

## 系统

### health()

健康检查

```python
result = tdx.health()
```

**返回值**: dict

---

### get_server_status()

获取服务状态

```python
result = tdx.get_server_status()
```

**返回值**: dict

---

## 异常

tdxdata定义了以下异常类：

| 异常 | 说明 |
|------|------|
| TDXError | 基础异常 |
| TDXConnectionError | 连接失败 |
| TDXAPIError | API返回错误 |
| TDXDataError | 数据错误 |
| TDXAuthError | 认证失败 |

```python
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

---

## 数据单位

| 数据类型 | API返回 | Python包返回 |
|----------|---------|--------------|
| 价格 | 厘 | 元 (÷1000) |
| 成交量 | 手 | 手 |
| 成交额 | 厘 | 元 (÷1000) |

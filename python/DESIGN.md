# tdxdata Python包设计文档

## 1. 概述

### 1.1 项目背景

tdxdata 是一个基于通达信(TDX)协议的A股数据查询Python包，封装了tdx-api项目的全部32个RESTful接口，提供类jqdata风格的函数式接口。

### 1.2 设计目标

- **类jqdata风格**：直接函数调用，无需实例化客户端
- **覆盖全部接口**：32个API接口完整封装
- **返回DataFrame**：主要数据接口返回pandas.DataFrame
- **零配置使用**：连接信息写死在代码中
- **类型提示完整**：支持IDE自动补全

### 1.3 连接配置

```python
DEFAULT_HOST = "100.107.142.74"
DEFAULT_PORT = 8080
BASE_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"
```

---

## 2. 项目结构

```
python/
├── tdxdata/
│   ├── __init__.py          # 包导出，类jqdata风格
│   ├── api.py               # API函数接口（上层）
│   ├── client.py            # 客户端实现（核心）
│   ├── config.py            # 配置（写死连接信息）
│   ├── models.py            # 数据模型
│   ├── exceptions.py        # 异常定义
│   └── utils.py             # 工具函数
├── tests/
│   └── test_api.py          # 测试用例
├── pyproject.toml           # 包配置
├── requirements.txt         # 依赖
├── requirements-dev.txt     # 开发依赖
├── README.md                # 使用手册
└── API.md                  # API文档
```

---

## 3. API接口映射

### 3.1 基础接口 (6个)

| API路径 | 函数名 | 返回类型 | 说明 |
|---------|--------|----------|------|
| `/api/quote` | `get_quote()` | DataFrame | 五档行情 |
| `/api/kline` | `get_kline()` | DataFrame | K线数据 |
| `/api/minute` | `get_minute()` | DataFrame | 分时数据 |
| `/api/trade` | `get_trade()` | DataFrame | 逐笔成交 |
| `/api/search` | `search_stock()` | DataFrame | 股票搜索 |
| `/api/stock-info` | `get_stock_info()` | dict | 综合信息 |

### 3.2 扩展接口 (26个)

| API路径 | 函数名 | 返回类型 | 说明 |
|---------|--------|----------|------|
| `/api/codes` | `get_stock_list()` | dict | 股票列表 |
| `/api/batch-quote` | `batch_quote()` | dict | 批量行情 |
| `/api/kline-history` | `get_kline_history()` | DataFrame | 历史K线 |
| `/api/index` | `get_index()` | DataFrame | 指数K线 |
| `/api/server-status` | `get_server_status()` | dict | 服务状态 |
| `/api/tasks/pull-kline` | `create_kline_task()` | str | 创建K线任务 |
| `/api/tasks/pull-trade` | `create_trade_task()` | str | 创建成交任务 |
| `/api/tasks` | `list_tasks()` | list | 任务列表 |
| `/api/tasks/{id}` | `get_task()` | dict | 任务详情 |
| `/api/tasks/{id}/cancel` | `cancel_task()` | dict | 取消任务 |
| `/api/etf` | `get_etf_list()` | dict | ETF列表 |
| `/api/trade-history` | `get_trade_history()` | dict | 历史分时成交 |
| `/api/minute-trade-all` | `get_minute_trade_all()` | dict | 全天分时成交 |
| `/api/workday` | `get_workday_info()` | dict | 交易日信息 |
| `/api/market-count` | `get_market_count()` | dict | 市场证券数量 |
| `/api/stock-codes` | `get_stock_codes()` | dict | 股票代码列表 |
| `/api/etf-codes` | `get_etf_codes()` | dict | ETF代码列表 |
| `/api/kline-all` | `get_kline_all()` | dict | 全量历史K线 |
| `/api/index/all` | `get_index_all()` | dict | 指数全量K线 |
| `/api/trade-history/full` | `get_trade_history_full()` | dict | 全部分时成交 |
| `/api/workday/range` | `get_workday_range()` | dict | 交易日范围 |
| `/api/income` | `get_income()` | dict | 收益区间 |
| `/api/kline-all/tdx` | `get_kline_all_tdx()` | dict | TDX原始K线 |
| `/api/kline-all/ths` | `get_kline_all_ths()` | dict | THS前复权K线 |
| `/api/health` | `health()` | dict | 健康检查 |
| `/api/market-stats` | `get_market_stats()` | dict | 市场统计 |

---

## 4. 数据模型

### 4.1 Quote（五档行情）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | str | 股票代码 |
| name | str | 股票名称 |
| exchange | str | 交易所 |
| last | float | 昨收价(元) |
| open | float | 开盘价(元) |
| high | float | 最高价(元) |
| low | float | 最低价(元) |
| close | float | 最新价(元) |
| volume | int | 成交量(手) |
| amount | float | 成交额(元) |
| buy1-5 | float | 买一~买五价(元) |
| sell1-5 | float | 卖一~卖五价(元) |
| buy1-5_vol | int | 买一~买五量(手) |
| sell1-5_vol | int | 卖一~卖五量(手) |

### 4.2 Kline（K线）

| 字段 | 类型 | 说明 |
|------|------|------|
| time | datetime | 时间 |
| open | float | 开盘价(元) |
| high | float | 最高价(元) |
| low | float | 最低价(元) |
| close | float | 收盘价(元) |
| volume | int | 成交量(手) |
| amount | float | 成交额(元) |

### 4.3 Minute（分时）

| 字段 | 类型 | 说明 |
|------|------|------|
| time | str | 时间(HH:MM) |
| price | float | 价格(元) |
| volume | int | 成交量(手) |

### 4.4 Trade（逐笔成交）

| 字段 | 类型 | 说明 |
|------|------|------|
| time | datetime | 时间 |
| price | float | 成交价(元) |
| volume | int | 成交量(手) |
| status | int | 0=买入,1=卖出,2=中性 |

---

## 5. 函数签名设计

### 5.1 核心函数

```python
# ========== 行情数据 ==========
def get_quote(code: str) -> DataFrame:
    """获取五档行情，支持逗号分隔多代码"""

def get_kline(code: str, period: str = "day", limit: int = 100) -> DataFrame:
    """获取K线数据，period: minute1/5/15/30/hour/day/week/month"""

def get_minute(code: str, date: str = None) -> DataFrame:
    """获取分时数据，date: YYYYMMDD格式"""

def get_trade(code: str, date: str = None) -> DataFrame:
    """获取逐笔成交"""

def search_stock(keyword: str) -> DataFrame:
    """搜索股票，返回code/name/exchange"""

def get_stock_info(code: str) -> dict:
    """获取股票综合信息(五档+K线+分时)"""

# ========== 批量接口 ==========
def batch_quote(codes: List[str]) -> dict:
    """批量获取行情"""

def get_stock_list(exchange: str = "all") -> dict:
    """获取股票列表，exchange: sh/sz/bj/all"""

# ========== K线扩展 ==========
def get_kline_history(code: str, period: str = "day",
                      start_date: str = None, end_date: str = None,
                      limit: int = 100) -> DataFrame:
    """获取指定时间范围K线"""

def get_kline_all(code: str, period: str = "day", limit: int = None) -> dict:
    """获取全量历史K线"""

def get_kline_all_tdx(code: str, period: str = "day", limit: int = None) -> dict:
    """获取通达信原始K线"""

def get_kline_all_ths(code: str, period: str = "day", limit: int = None) -> dict:
    """获取同花顺前复权K线"""

# ========== 指数 ==========
def get_index(code: str, period: str = "day") -> DataFrame:
    """获取指数K线，code如: sh000001"""

def get_index_all(code: str, period: str = "day", limit: int = None) -> dict:
    """获取指数全量K线"""

# ========== 分时成交 ==========
def get_trade_history(code: str, date: str, start: int = 0,
                      count: int = 2000) -> dict:
    """历史分时成交(分页)"""

def get_minute_trade_all(code: str, date: str = None) -> dict:
    """全天分时成交"""

def get_trade_history_full(code: str, before: str = None,
                           limit: int = None) -> dict:
    """上市以来全部分时成交"""

# ========== ETF ==========
def get_etf_list(exchange: str = None, limit: int = None) -> dict:
    """获取ETF列表"""

def get_etf_codes(limit: int = None, prefix: bool = True) -> dict:
    """获取ETF代码列表"""

# ========== 股票代码 ==========
def get_stock_codes(limit: int = None, prefix: bool = True) -> dict:
    """获取股票代码列表"""

# ========== 交易日 ==========
def get_workday_info(date: str = None, count: int = 1) -> dict:
    """查询交易日信息"""

def get_workday_range(start: str, end: str) -> dict:
    """获取交易日范围"""

def is_workday(date: str = None) -> bool:
    """判断是否交易日"""

def get_next_workday(date: str = None, count: int = 1) -> list:
    """获取下一个交易日"""

def get_previous_workday(date: str = None, count: int = 1) -> list:
    """获取上一个交易日"""

# ========== 市场数据 ==========
def get_market_count() -> dict:
    """获取市场证券数量"""

def get_market_stats() -> dict:
    """获取市场统计"""

# ========== 收益分析 ==========
def get_income(code: str, start_date: str,
               days: str = "5,10,20,60,120") -> dict:
    """计算收益区间"""

# ========== 任务管理 ==========
def create_kline_task(codes: List[str] = None, tables: List[str] = None,
                      limit: int = 1, start_date: str = None) -> str:
    """创建K线入库任务"""

def create_trade_task(code: str, start_year: int = 2000,
                      end_year: int = None) -> str:
    """创建分时成交入库任务"""

def list_tasks() -> list:
    """获取任务列表"""

def get_task(task_id: str) -> dict:
    """获取任务详情"""

def cancel_task(task_id: str) -> dict:
    """取消任务"""

# ========== 系统 ==========
def health() -> dict:
    """健康检查"""

def get_server_status() -> dict:
    """获取服务状态"""

# ========== 初始化 ==========
def auth() -> None:
    """初始化连接，类似jqdata.auth()"""
```

---

## 6. 单位换算规则

| 数据类型 | API返回单位 | Python包返回单位 |
|----------|------------|-----------------|
| 价格 | 厘 | 元 (÷1000) |
| 成交量 | 手 | 手 |
| 成交额 | 厘 | 元 (÷1000) |
| 挂单量 | 股 | 手 (÷100) |

---

## 7. 异常处理

```python
class TDXError(Exception):
    """基础异常"""
    pass

class TDXConnectionError(TDXError):
    """连接失败"""
    pass

class TDXAPIError(TDXError):
    """API返回错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

class TDXDataError(TDXError):
    """数据错误"""
    pass
```

---

## 8. 使用示例

```python
import tdxdata as tdx

# 初始化
tdx.auth()

# 行情
df = tdx.get_quote("000001")
df = tdx.get_quote("000001,600519")

# K线
df = tdx.get_kline("000001", period="day", limit=100)
df = tdx.get_kline("000001", period="minute15", limit=200)

# 分时
df = tdx.get_minute("000001")
df = tdx.get_minute("000001", "20241103")

# 搜索
df = tdx.search_stock("茅台")

# 批量
quotes = tdx.batch_quote(["000001", "600519"])

# 指数
df = tdx.get_index("sh000001")

# ETF
etfs = tdx.get_etf_list(exchange="sh", limit=10)

# 交易日
info = tdx.get_workday_info("20241103")
is_today = tdx.is_workday()

# 批量入库
task_id = tdx.create_kline_task(["000001"], tables=["day", "week"])
tasks = tdx.list_tasks()
```

---

## 9. 版本规划

- v0.1.0: 初始版本，包含全部32个API接口
- 后续: 考虑添加异步客户端、缓存机制

---

## 10. 注意事项

1. 价格单位转换：API返回厘，需除以1000转为元
2. 成交量单位：API返回手，直接使用
3. 日期格式：YYYYMMDD 或 YYYY-MM-DD
4. 全量K线接口数据量大，建议设置limit
5. 非交易时间分时数据不可用

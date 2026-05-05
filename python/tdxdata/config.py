# -*- coding: utf-8 -*-
"""
tdxdata 配置模块
连接信息写死在代码中
"""

# 默认连接地址（个人使用，直接写死）
DEFAULT_HOST = "100.107.142.74"
DEFAULT_PORT = 8080
BASE_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"

# 请求超时时间（秒）
TIMEOUT = 30

# 全局客户端实例
_client = None


def init():
    """初始化全局客户端"""
    global _client
    from .client import Client
    _client = Client(BASE_URL)
    return _client


def get_client():
    """获取全局客户端，懒加载"""
    if _client is None:
        init()
    return _client


def set_client(client):
    """设置全局客户端（用于测试）"""
    global _client
    _client = client

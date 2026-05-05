# -*- coding: utf-8 -*-
"""
tdxdata 异常定义
"""


class TDXError(Exception):
    """tdxdata基础异常"""
    pass


class TDXConnectionError(TDXError):
    """连接失败异常"""
    pass


class TDXAPIError(TDXError):
    """API返回错误异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API错误 [{code}]: {message}")


class TDXDataError(TDXError):
    """数据错误异常"""
    pass


class TDXAuthError(TDXError):
    """认证失败异常"""
    pass

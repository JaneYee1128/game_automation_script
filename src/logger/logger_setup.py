"""
日志设置模块
提供统一的日志系统设置和初始化功能
"""

import logging
from typing import List, Optional, Union

def init_logging(
    level: Union[int, str] = logging.INFO,
    handlers: Optional[List[logging.Handler]] = None,
    propagate: bool = False
) -> None:
    """
    初始化日志系统
    
    参数:
        level: 日志级别，可以是logging模块定义的级别常量或对应的字符串
        handlers: 日志处理器列表，如果为None则创建默认的控制台处理器
        propagate: 是否传播日志记录到父级logger
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 设置日志级别
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加新的处理器
    if handlers:
        for handler in handlers:
            root_logger.addHandler(handler)
    else:
        # 创建默认的控制台处理器
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 设置是否传播
    root_logger.propagate = propagate
    
    # 记录初始化完成
    root_logger.debug("日志系统初始化完成")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    参数:
        name: 日志记录器名称
    
    返回:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)

"""
使用示例：

from logger.logger_setup import init_logging, get_logger

# 初始化日志系统
init_logging(level="DEBUG")

# 获取日志记录器
logger = get_logger(__name__)

# 记录日志
logger.debug("这是一条调试日志")
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.critical("这是一条严重错误日志")
"""
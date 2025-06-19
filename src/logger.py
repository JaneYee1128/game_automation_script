"""
日志系统模块
配置统一的日志格式和级别，支持日志文件轮转和控制台输出
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time
from typing import Optional, Dict, Any, Union

from config import config

class LoggerSetup:
    """日志设置类，用于配置和管理日志系统"""
    
    # 默认日志格式
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 日志级别映射
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self):
        """初始化日志设置"""
        # 确保日志目录存在
        self.logs_path = config.logs_path
        os.makedirs(self.logs_path, exist_ok=True)
        
        # 获取配置
        self.log_level = config.get("log_level", "INFO")
        self.log_format = config.get("log_format", self.DEFAULT_FORMAT)
        self.log_to_console = config.get("log_to_console", True)
        self.log_to_file = config.get("log_to_file", True)
        self.log_file_max_size = config.get("log_file_max_size", 10 * 1024 * 1024)  # 10MB
        self.log_file_backup_count = config.get("log_file_backup_count", 5)
        self.log_file_rotation = config.get("log_file_rotation", "size")  # size or time
        
        # 根日志记录器
        self.root_logger = logging.getLogger()
        
        # 已配置的日志记录器
        self.configured_loggers = set()
    
    def setup_root_logger(self) -> None:
        """设置根日志记录器"""
        # 设置日志级别
        level = self.LOG_LEVELS.get(self.log_level.upper(), logging.INFO)
        self.root_logger.setLevel(level)
        
        # 清除现有处理器
        for handler in self.root_logger.handlers[:]:
            self.root_logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(self.log_format)
        
        # 添加控制台处理器
        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.root_logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self.log_to_file:
            # 确定日志文件名
            timestamp = time.strftime('%Y%m%d')
            log_file = os.path.join(self.logs_path, f"game_automation_{timestamp}.log")
            
            # 根据配置选择轮转方式
            if self.log_file_rotation == "time":
                file_handler = TimedRotatingFileHandler(
                    log_file,
                    when='midnight',
                    interval=1,
                    backupCount=self.log_file_backup_count
                )
            else:  # size
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=self.log_file_max_size,
                    backupCount=self.log_file_backup_count
                )
            
            file_handler.setFormatter(formatter)
            self.root_logger.addHandler(file_handler)
        
        logging.info("日志系统已初始化")
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        参数:
            name: 日志记录器名称
            level: 日志级别，None则使用默认级别
        
        返回:
            logging.Logger: 日志记录器
        """
        logger = logging.getLogger(name)
        
        # 如果指定了级别，设置级别
        if level:
            logger.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))
        
        # 记录已配置的日志记录器
        self.configured_loggers.add(name)
        
        return logger
    
    def set_level(self, level: str, logger_name: Optional[str] = None) -> bool:
        """
        设置日志级别
        
        参数:
            level: 日志级别
            logger_name: 日志记录器名称，None则设置根日志记录器
        
        返回:
            bool: 是否成功设置
        """
        try:
            log_level = self.LOG_LEVELS.get(level.upper())
            if not log_level:
                return False
            
            if logger_name:
                logger = logging.getLogger(logger_name)
                logger.setLevel(log_level)
            else:
                self.root_logger.setLevel(log_level)
                
                # 更新配置
                self.log_level = level.upper()
            
            return True
        except Exception as e:
            logging.error(f"设置日志级别失败: {str(e)}")
            return False
    
    def add_file_handler(self, logger_name: str, file_path: str, 
                        level: Optional[str] = None, 
                        rotation: str = "size",
                        max_size: int = 10 * 1024 * 1024,
                        backup_count: int = 5) -> bool:
        """
        为指定日志记录器添加文件处理器
        
        参数:
            logger_name: 日志记录器名称
            file_path: 日志文件路径
            level: 日志级别，None则使用默认级别
            rotation: 轮转方式，"size"或"time"
            max_size: 最大文件大小（字节）
            backup_count: 备份文件数量
        
        返回:
            bool: 是否成功添加
        """
        try:
            logger = logging.getLogger(logger_name)
            
            # 创建格式化器
            formatter = logging.Formatter(self.log_format)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 创建文件处理器
            if rotation == "time":
                handler = TimedRotatingFileHandler(
                    file_path,
                    when='midnight',
                    interval=1,
                    backupCount=backup_count
                )
            else:  # size
                handler = RotatingFileHandler(
                    file_path,
                    maxBytes=max_size,
                    backupCount=backup_count
                )
            
            # 设置格式和级别
            handler.setFormatter(formatter)
            if level:
                handler.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))
            
            # 添加处理器
            logger.addHandler(handler)
            
            return True
        except Exception as e:
            logging.error(f"添加文件处理器失败: {str(e)}")
            return False
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """
        获取所有已配置的日志记录器
        
        返回:
            Dict[str, logging.Logger]: 日志记录器字典
        """
        loggers = {}
        for name in self.configured_loggers:
            loggers[name] = logging.getLogger(name)
        return loggers

# 创建全局日志设置实例
logger_setup = LoggerSetup()

# 初始化根日志记录器
logger_setup.setup_root_logger()

"""
使用示例：

# 获取日志记录器
from logger import logger_setup

# 获取默认级别的日志记录器
logger = logger_setup.get_logger('MyModule')
logger.info('这是一条信息日志')
logger.error('这是一条错误日志')

# 获取指定级别的日志记录器
debug_logger = logger_setup.get_logger('DebugModule', 'DEBUG')
debug_logger.debug('这是一条调试日志')

# 修改日志级别
logger_setup.set_level('DEBUG')  # 设置根日志记录器级别
logger_setup.set_level('ERROR', 'MyModule')  # 设置特定日志记录器级别

# 添加文件处理器
logger_setup.add_file_handler('MyModule', 'logs/my_module.log', 'DEBUG')
"""
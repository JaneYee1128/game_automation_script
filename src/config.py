"""
配置模块
管理系统的各种配置项，包括路径、日志级别等
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Union

class Config:
    """配置类，用于管理系统配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 日志配置
        "log_level": "INFO",
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "log_to_console": True,
        "log_to_file": True,
        "log_file_max_size": 10 * 1024 * 1024,  # 10MB
        "log_file_backup_count": 5,
        "log_file_rotation": "size",  # size or time
        
        # 路径配置
        "paths": {
            "scripts": "scripts",
            "recordings": "recordings",
            "screenshots": "screenshots",
            "templates": "templates",
            "logs": "logs"
        },
        
        # 录制配置
        "recording": {
            "include_mouse": True,
            "include_keyboard": True,
            "include_windows": True
        },
        
        # 回放配置
        "playback": {
            "default_speed": 1.0,
            "wait_for_images": True,
            "image_match_threshold": 0.8
        },
        
        # 图像识别配置
        "image_recognition": {
            "method": "template_matching",  # template_matching, feature_matching, or deep_learning
            "match_threshold": 0.8,
            "max_wait_time": 10.0  # 最大等待时间（秒）
        },
        
        # GUI配置
        "gui": {
            "theme": "system",  # system, light, or dark
            "font_size": 10,
            "window_size": [1000, 700],
            "window_position": [100, 100]
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置
        
        参数:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 加载配置文件
        self.load_config()
        
        # 确保目录存在
        self._ensure_directories()
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        返回:
            bool: 是否成功加载
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 递归更新配置
                self._update_dict(self.config, loaded_config)
                
                logging.info(f"已加载配置文件: {self.config_file}")
                return True
            else:
                logging.warning(f"配置文件不存在，使用默认配置: {self.config_file}")
                return False
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        返回:
            bool: 是否成功保存
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logging.info(f"已保存配置文件: {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        参数:
            key: 配置项键，支持点号分隔的路径，如 'paths.scripts'
            default: 默认值，如果配置项不存在则返回此值
        
        返回:
            Any: 配置项值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置项
        
        参数:
            key: 配置项键，支持点号分隔的路径，如 'paths.scripts'
            value: 配置项值
        
        返回:
            bool: 是否成功设置
        """
        keys = key.split('.')
        config = self.config
        
        # 遍历到最后一个键之前的所有键
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置最后一个键的值
        config[keys[-1]] = value
        return True
    
    def _update_dict(self, target: Dict, source: Dict) -> None:
        """
        递归更新字典
        
        参数:
            target: 目标字典
            source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value
    
    def _ensure_directories(self) -> None:
        """确保所有配置的目录都存在"""
        paths = self.get("paths", {})
        for name, path in paths.items():
            os.makedirs(path, exist_ok=True)
    
    @property
    def scripts_path(self) -> str:
        """脚本路径"""
        return self.get("paths.scripts", "scripts")
    
    @property
    def recordings_path(self) -> str:
        """录制文件路径"""
        return self.get("paths.recordings", "recordings")
    
    @property
    def screenshots_path(self) -> str:
        """截图路径"""
        return self.get("paths.screenshots", "screenshots")
    
    @property
    def templates_path(self) -> str:
        """模板路径"""
        return self.get("paths.templates", "templates")
    
    @property
    def logs_path(self) -> str:
        """日志路径"""
        return self.get("paths.logs", "logs")

# 创建全局配置实例
config = Config()

"""
使用示例：

from config import config

# 获取配置项
log_level = config.get("log_level")
scripts_path = config.scripts_path

# 设置配置项
config.set("log_level", "DEBUG")
config.set("paths.scripts", "new_scripts_path")

# 保存配置
config.save_config()
"""
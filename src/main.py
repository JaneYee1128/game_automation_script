"""
主入口模块
用于启动游戏自动化脚本系统的GUI应用程序
"""

import os
import sys
import logging
from PyQt5.QtWidgets import QApplication

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# 导入项目模块
from config import config
from logger import logger_setup
from gui.main_window import MainWindow

def init_logging():
    """初始化日志系统"""
    # 设置日志级别
    log_level = getattr(logging, config.get("log_level", "INFO"))
    
    # 设置日志格式
    log_format = config.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # 设置日志处理器
    handlers = []
    
    # 控制台处理器
    if config.get("log_to_console", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
    
    # 文件处理器
    if config.get("log_to_file", True):
        from logging.handlers import RotatingFileHandler
        
        log_file = os.path.join(config.logs_path, "app.log")
        max_size = config.get("log_file_max_size", 10 * 1024 * 1024)  # 默认10MB
        backup_count = config.get("log_file_backup_count", 5)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # 初始化日志系统
    logger_setup.init_logging(log_level, handlers)

def init_directories():
    """初始化必要的目录"""
    directories = [
        config.scripts_path,
        config.recordings_path,
        config.screenshots_path,
        config.templates_path,
        config.logs_path
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.debug(f"确保目录存在: {directory}")
        except Exception as e:
            logging.error(f"创建目录失败 {directory}: {str(e)}")

def init_app():
    """初始化应用程序"""
    # 初始化日志系统
    init_logging()
    
    # 初始化目录
    init_directories()
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("游戏自动化脚本系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Game Automation")
    app.setOrganizationDomain("gameautomation.org")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    return app, window

def main():
    """主函数"""
    try:
        # 初始化应用程序
        app, window = init_app()
        
        # 记录启动信息
        logging.info("应用程序已启动")
        
        # 运行应用程序
        exit_code = app.exec_()
        
        # 记录退出信息
        logging.info(f"应用程序已退出，退出码: {exit_code}")
        
        # 返回退出码
        return exit_code
    
    except Exception as e:
        logging.critical(f"应用程序发生严重错误: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
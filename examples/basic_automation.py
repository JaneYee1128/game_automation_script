"""
基本自动化示例脚本

展示如何使用游戏自动化脚本工具进行基本的自动化操作
"""

import os
import sys
import time
import logging

# 添加父目录到系统路径，以便导入src包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
from src.event_player import EventPlayer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BasicAutomation')

def main():
    """基本自动化示例"""
    logger.info("启动基本自动化示例")
    
    # 初始化屏幕捕获
    screen_capture = ScreenCapture()
    
    # 初始化图像识别
    image_recognition = ImageRecognition()
    
    # 初始化事件播放器
    event_player = EventPlayer()
    
    try:
        # 示例1：捕获屏幕并保存
        logger.info("示例1：捕获屏幕并保存")
        screen = screen_capture.capture_screen()
        screen_capture.save_screen(screen, "example_screen.png")
        logger.info("屏幕已保存为 example_screen.png")
        
        # 等待2秒
        time.sleep(2)
        
        # 示例2：加载并回放录制的事件
        logger.info("示例2：尝试加载并回放录制的事件")
        recordings = event_player.get_recordings_list()
        if recordings:
            recording_name = recordings[0]
            logger.info(f"找到录制: {recording_name}")
            
            if event_player.load_recording(recording_name):
                logger.info(f"加载录制: {recording_name}")
                logger.info("开始回放...")
                event_player.start_playback()
                
                # 等待回放完成
                while event_player.is_playing():
                    time.sleep(0.5)
                
                logger.info("回放完成")
            else:
                logger.warning("无法加载录制")
        else:
            logger.warning("未找到录制文件，请先使用GUI创建录制")
        
        # 示例3：尝试进行图像识别
        logger.info("示例3：尝试进行图像识别")
        templates = image_recognition.templates
        if templates:
            template_name = list(templates.keys())[0]
            logger.info(f"找到模板: {template_name}")
            
            screen = screen_capture.capture_screen()
            locations = image_recognition.find_template(screen, template_name)
            
            if locations:
                logger.info(f"找到 {len(locations)} 个匹配")
                for i, (x, y, w, h, conf) in enumerate(locations):
                    logger.info(f"匹配 {i+1}: 位置=({x}, {y}), 大小={w}x{h}, 置信度={conf:.2f}")
            else:
                logger.info("未找到匹配")
        else:
            logger.warning("未找到模板文件，请先使用GUI创建模板")
        
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
    
    logger.info("示例结束")

if __name__ == "__main__":
    main()
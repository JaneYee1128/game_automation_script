"""
事件播放器模块
回放记录的鼠标和键盘操作
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from threading import Thread, Event

import pyautogui
from PIL import Image

from config import config
from image_recognition import ImageRecognition
from screen_capture import ScreenCapture

logger = logging.getLogger('EventPlayer')

class EventPlayer:
    """事件播放器类，回放记录的鼠标和键盘操作"""
    
    def __init__(self):
        """初始化事件播放器"""
        # 播放状态
        self.playing = False
        self.paused = False
        self._stop_event = Event()
        
        # 事件列表
        self.events: List[Dict[str, Any]] = []
        
        # 播放线程
        self.playback_thread = None
        
        # 播放配置
        self.speed = config.get("playback.default_speed", 1.0)
        self.retry_attempts = config.get("playback.retry_attempts", 3)
        self.retry_delay = config.get("playback.retry_delay", 1.0)
        self.wait_for_images = config.get("playback.wait_for_images", True)
        
        # 图像识别和屏幕捕获
        self.image_recognition = ImageRecognition()
        self.screen_capture = ScreenCapture()
        
        # 回调函数
        self.on_start = None
        self.on_stop = None
        self.on_pause = None
        self.on_resume = None
        self.on_event = None
        self.on_error = None
    
    def load_recording(self, file_path: str) -> bool:
        """
        加载录制文件
        
        参数:
            file_path: 录制文件路径
        
        返回:
            bool: 是否成功加载
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                recording_data = json.load(f)
            
            # 验证数据格式
            if "events" not in recording_data:
                logger.error("无效的录制文件格式")
                return False
            
            self.events = recording_data["events"]
            logger.info(f"已加载录制文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"加载录制文件失败: {str(e)}")
            return False
    
    def start_playback(self, speed: float = None) -> bool:
        """
        开始回放
        
        参数:
            speed: 回放速度，None则使用默认速度
        
        返回:
            bool: 是否成功开始回放
        """
        if self.playing:
            logger.warning("播放器已经在运行")
            return False
        
        if not self.events:
            logger.error("没有加载录制文件")
            return False
        
        try:
            # 设置回放速度
            if speed is not None:
                self.speed = speed
            
            # 重置状态
            self.playing = True
            self.paused = False
            self._stop_event.clear()
            
            # 启动回放线程
            self.playback_thread = Thread(target=self._playback_loop)
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
            logger.info(f"开始回放，速度: {self.speed}")
            
            # 调用回调函数
            if self.on_start:
                self.on_start()
            
            return True
        except Exception as e:
            logger.error(f"启动播放器失败: {str(e)}")
            self.stop_playback()
            return False
    
    def stop_playback(self) -> bool:
        """
        停止回放
        
        返回:
            bool: 是否成功停止回放
        """
        if not self.playing:
            return False
        
        try:
            # 设置停止标志
            self._stop_event.set()
            self.playing = False
            
            # 等待回放线程结束
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join()
                self.playback_thread = None
            
            logger.info("停止回放")
            
            # 调用回调函数
            if self.on_stop:
                self.on_stop()
            
            return True
        except Exception as e:
            logger.error(f"停止播放器失败: {str(e)}")
            return False
    
    def pause_playback(self) -> bool:
        """
        暂停回放
        
        返回:
            bool: 是否成功暂停回放
        """
        if not self.playing or self.paused:
            return False
        
        self.paused = True
        logger.info("暂停回放")
        
        # 调用回调函数
        if self.on_pause:
            self.on_pause()
        
        return True
    
    def resume_playback(self) -> bool:
        """
        恢复回放
        
        返回:
            bool: 是否成功恢复回放
        """
        if not self.playing or not self.paused:
            return False
        
        self.paused = False
        logger.info("恢复回放")
        
        # 调用回调函数
        if self.on_resume:
            self.on_resume()
        
        return True
    
    def _playback_loop(self) -> None:
        """回放循环"""
        try:
            # 设置安全模式
            pyautogui.FAILSAFE = True
            
            # 初始化时间
            start_time = time.time()
            last_event_time = 0
            
            # 遍历事件
            for i, event in enumerate(self.events):
                # 检查是否停止
                if self._stop_event.is_set():
                    break
                
                # 检查是否暂停
                while self.paused and not self._stop_event.is_set():
                    time.sleep(0.1)
                
                if self._stop_event.is_set():
                    break
                
                # 计算等待时间
                event_time = event["time"]
                wait_time = (event_time - last_event_time) / self.speed
                
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # 执行事件
                success = self._execute_event(event)
                
                # 调用事件回调
                if self.on_event:
                    self.on_event(i, event, success)
                
                # 更新上一个事件时间
                last_event_time = event_time
            
            logger.info("回放完成")
        except Exception as e:
            logger.error(f"回放过程中出错: {str(e)}")
            
            # 调用错误回调
            if self.on_error:
                self.on_error(str(e))
        finally:
            self.playing = False
            
            # 调用停止回调
            if self.on_stop:
                self.on_stop()
    
    def _execute_event(self, event: Dict[str, Any]) -> bool:
        """
        执行单个事件
        
        参数:
            event: 事件数据
        
        返回:
            bool: 是否成功执行
        """
        try:
            event_type = event["type"]
            
            if event_type == "mouse_move":
                return self._execute_mouse_move(event)
            elif event_type == "mouse_click":
                return self._execute_mouse_click(event)
            elif event_type == "mouse_scroll":
                return self._execute_mouse_scroll(event)
            elif event_type == "key_press":
                return self._execute_key_press(event)
            elif event_type == "key_release":
                return self._execute_key_release(event)
            elif event_type == "wait_for_image":
                return self._execute_wait_for_image(event)
            else:
                logger.warning(f"未知的事件类型: {event_type}")
                return False
        except Exception as e:
            logger.error(f"执行事件失败: {str(e)}")
            return False
    
    def _execute_mouse_move(self, event: Dict[str, Any]) -> bool:
        """执行鼠标移动事件"""
        try:
            x = event["x"]
            y = event["y"]
            
            # 移动鼠标
            pyautogui.moveTo(x, y)
            return True
        except Exception as e:
            logger.error(f"执行鼠标移动事件失败: {str(e)}")
            return False
    
    def _execute_mouse_click(self, event: Dict[str, Any]) -> bool:
        """执行鼠标点击事件"""
        try:
            x = event["x"]
            y = event["y"]
            button = event["button"]
            pressed = event["pressed"]
            
            if pressed:
                # 按下鼠标按钮
                pyautogui.mouseDown(x=x, y=y, button=button)
            else:
                # 释放鼠标按钮
                pyautogui.mouseUp(x=x, y=y, button=button)
            
            return True
        except Exception as e:
            logger.error(f"执行鼠标点击事件失败: {str(e)}")
            return False
    
    def _execute_mouse_scroll(self, event: Dict[str, Any]) -> bool:
        """执行鼠标滚轮事件"""
        try:
            dx = event["dx"]
            dy = event["dy"]
            
            # 滚动鼠标滚轮
            pyautogui.scroll(dy * 100)  # 放大滚动量
            
            return True
        except Exception as e:
            logger.error(f"执行鼠标滚轮事件失败: {str(e)}")
            return False
    
    def _execute_key_press(self, event: Dict[str, Any]) -> bool:
        """执行键盘按下事件"""
        try:
            key = event["key"]
            
            # 按下按键
            pyautogui.keyDown(key)
            
            return True
        except Exception as e:
            logger.error(f"执行键盘按下事件失败: {str(e)}")
            return False
    
    def _execute_key_release(self, event: Dict[str, Any]) -> bool:
        """执行键盘释放事件"""
        try:
            key = event["key"]
            
            # 释放按键
            pyautogui.keyUp(key)
            
            return True
        except Exception as e:
            logger.error(f"执行键盘释放事件失败: {str(e)}")
            return False
    
    def _execute_wait_for_image(self, event: Dict[str, Any]) -> bool:
        """执行等待图像事件"""
        try:
            image_path = event["image_path"]
            timeout = event.get("timeout", 10.0)
            confidence = event.get("confidence", config.match_threshold)
            
            # 确保图像路径存在
            if not os.path.isabs(image_path):
                image_path = os.path.join(config.templates_path, image_path)
            
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return False
            
            # 等待图像出现
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查是否停止
                if self._stop_event.is_set():
                    return False
                
                # 捕获屏幕
                screenshot = self.screen_capture.capture()
                
                # 查找图像
                result = self.image_recognition.find_template(screenshot, image_path, confidence)
                
                if result:
                    logger.debug(f"找到图像: {image_path}")
                    return True
                
                # 等待一段时间
                time.sleep(0.5)
            
            logger.warning(f"等待图像超时: {image_path}")
            return False
        except Exception as e:
            logger.error(f"执行等待图像事件失败: {str(e)}")
            return False
    
    def add_wait_for_image(self, image_path: str, timeout: float = 10.0, confidence: float = None) -> bool:
        """
        添加等待图像事件
        
        参数:
            image_path: 图像路径
            timeout: 超时时间（秒）
            confidence: 匹配阈值（0-1），None则使用默认值
        
        返回:
            bool: 是否成功添加
        """
        try:
            # 创建等待图像事件
            event = {
                "type": "wait_for_image",
                "time": time.time(),
                "image_path": image_path,
                "timeout": timeout,
                "confidence": confidence or config.match_threshold
            }
            
            # 添加到事件列表
            self.events.append(event)
            
            return True
        except Exception as e:
            logger.error(f"添加等待图像事件失败: {str(e)}")
            return False

"""
使用示例：

# 创建事件播放器实例
player = EventPlayer()

# 设置回调函数
def on_start():
    print("开始回放")

def on_stop():
    print("停止回放")

def on_event(index, event, success):
    print(f"事件 {index}: {event['type']} - {'成功' if success else '失败'}")

player.on_start = on_start
player.on_stop = on_stop
player.on_event = on_event

# 加载录制文件
player.load_recording("my_recording.json")

# 开始回放
player.start_playback(speed=1.5)

# 等待回放完成
while player.playing:
    time.sleep(0.1)
"""
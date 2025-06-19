"""
事件记录器模块
记录用户的鼠标和键盘操作
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from threading import Thread, Event, Lock
from pynput import mouse, keyboard
from datetime import datetime

from config import config

logger = logging.getLogger('EventRecorder')

class EventRecorder:
    """事件记录器类，记录用户的鼠标和键盘操作"""
    
    def __init__(self):
        """初始化事件记录器"""
        # 记录状态
        self.recording = False
        self.paused = False
        self._stop_event = Event()
        
        # 事件列表和锁
        self.events: List[Dict[str, Any]] = []
        self.events_lock = Lock()
        
        # 监听器
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # 自动保存
        self.auto_save = config.get("recording.auto_save", True)
        self.save_interval = config.get("recording.save_interval", 30)
        self.auto_save_thread = None
        
        # 配置
        self.include_mouse = config.get("recording.include_mouse", True)
        self.include_keyboard = config.get("recording.include_keyboard", True)
        self.hotkey = config.get("recording.hotkey", "esc")
        
        # 记录开始时间
        self.start_time = 0
        
        # 回调函数
        self.on_start = None
        self.on_stop = None
        self.on_pause = None
        self.on_resume = None
    
    def start_recording(self) -> bool:
        """
        开始记录
        
        返回:
            bool: 是否成功开始记录
        """
        if self.recording:
            logger.warning("记录器已经在运行")
            return False
        
        try:
            # 清空事件列表
            with self.events_lock:
                self.events = []
            
            # 重置状态
            self.recording = True
            self.paused = False
            self._stop_event.clear()
            
            # 记录开始时间
            self.start_time = time.time()
            
            # 启动监听器
            if self.include_mouse:
                self.mouse_listener = mouse.Listener(
                    on_move=self._on_mouse_move,
                    on_click=self._on_mouse_click,
                    on_scroll=self._on_mouse_scroll
                )
                self.mouse_listener.start()
            
            if self.include_keyboard:
                self.keyboard_listener = keyboard.Listener(
                    on_press=self._on_key_press,
                    on_release=self._on_key_release
                )
                self.keyboard_listener.start()
            
            # 启动自动保存线程
            if self.auto_save:
                self.auto_save_thread = Thread(target=self._auto_save_loop)
                self.auto_save_thread.daemon = True
                self.auto_save_thread.start()
            
            logger.info("开始记录用户操作")
            
            # 调用回调函数
            if self.on_start:
                self.on_start()
            
            return True
        except Exception as e:
            logger.error(f"启动记录器失败: {str(e)}")
            self.stop_recording()
            return False
    
    def stop_recording(self) -> bool:
        """
        停止记录
        
        返回:
            bool: 是否成功停止记录
        """
        if not self.recording:
            return False
        
        try:
            # 设置停止标志
            self._stop_event.set()
            self.recording = False
            
            # 停止监听器
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            
            # 等待自动保存线程结束
            if self.auto_save_thread and self.auto_save_thread.is_alive():
                self.auto_save_thread.join()
                self.auto_save_thread = None
            
            logger.info("停止记录用户操作")
            
            # 调用回调函数
            if self.on_stop:
                self.on_stop()
            
            return True
        except Exception as e:
            logger.error(f"停止记录器失败: {str(e)}")
            return False
    
    def pause_recording(self) -> bool:
        """
        暂停记录
        
        返回:
            bool: 是否成功暂停记录
        """
        if not self.recording or self.paused:
            return False
        
        self.paused = True
        logger.info("暂停记录")
        
        # 调用回调函数
        if self.on_pause:
            self.on_pause()
        
        return True
    
    def resume_recording(self) -> bool:
        """
        恢复记录
        
        返回:
            bool: 是否成功恢复记录
        """
        if not self.recording or not self.paused:
            return False
        
        self.paused = False
        logger.info("恢复记录")
        
        # 调用回调函数
        if self.on_resume:
            self.on_resume()
        
        return True
    
    def save_recording(self, file_path: Optional[str] = None) -> bool:
        """
        保存记录
        
        参数:
            file_path: 保存路径，None则使用默认路径
        
        返回:
            bool: 是否成功保存
        """
        try:
            # 如果没有指定路径，使用默认路径
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(config.recordings_path, f"recording_{timestamp}.json")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 准备保存数据
            recording_data = {
                "version": "1.0",
                "start_time": self.start_time,
                "end_time": time.time(),
                "include_mouse": self.include_mouse,
                "include_keyboard": self.include_keyboard,
                "events": self.events
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recording_data, f, indent=2)
            
            logger.info(f"已保存记录到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存记录失败: {str(e)}")
            return False
    
    def _auto_save_loop(self) -> None:
        """自动保存循环"""
        last_save_time = time.time()
        
        while not self._stop_event.is_set():
            current_time = time.time()
            
            # 检查是否需要自动保存
            if current_time - last_save_time >= self.save_interval:
                if self.save_recording():
                    last_save_time = current_time
            
            # 等待一段时间
            self._stop_event.wait(1.0)
    
    def _add_event(self, event_type: str, **kwargs) -> None:
        """
        添加事件
        
        参数:
            event_type: 事件类型
            **kwargs: 事件参数
        """
        if not self.recording or self.paused:
            return
        
        # 创建事件数据
        event = {
            "type": event_type,
            "time": time.time() - self.start_time,
            **kwargs
        }
        
        # 添加到事件列表
        with self.events_lock:
            self.events.append(event)
    
    def _on_mouse_move(self, x: int, y: int) -> None:
        """鼠标移动事件处理"""
        self._add_event("mouse_move", x=x, y=y)
    
    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """鼠标点击事件处理"""
        # 转换按钮为字符串
        button_str = str(button).split('.')[-1]
        
        self._add_event(
            "mouse_click",
            x=x,
            y=y,
            button=button_str,
            pressed=pressed
        )
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """鼠标滚轮事件处理"""
        self._add_event(
            "mouse_scroll",
            x=x,
            y=y,
            dx=dx,
            dy=dy
        )
    
    def _on_key_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> None:
        """键盘按下事件处理"""
        # 检查是否是停止热键
        if hasattr(key, 'char'):
            key_str = key.char
        else:
            key_str = str(key).split('.')[-1]
        
        if key_str == self.hotkey:
            self.stop_recording()
            return
        
        self._add_event(
            "key_press",
            key=key_str
        )
    
    def _on_key_release(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> None:
        """键盘释放事件处理"""
        if hasattr(key, 'char'):
            key_str = key.char
        else:
            key_str = str(key).split('.')[-1]
        
        self._add_event(
            "key_release",
            key=key_str
        )

"""
使用示例：

# 创建事件记录器实例
recorder = EventRecorder()

# 设置回调函数
def on_start():
    print("开始记录")

def on_stop():
    print("停止记录")

recorder.on_start = on_start
recorder.on_stop = on_stop

# 开始记录
recorder.start_recording()

# 等待一段时间
time.sleep(10)

# 停止记录
recorder.stop_recording()

# 保存记录
recorder.save_recording("my_recording.json")
"""
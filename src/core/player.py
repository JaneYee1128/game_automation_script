"""
输入事件回放模块
提供录制事件的回放功能
"""

import os
import time
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable

# 用于模拟输入事件的库
import pyautogui
import keyboard
import mouse
import win32gui

# 导入项目模块
from logger import get_logger
from config import config
from core.recorder import (
    InputEvent,
    MouseEvent,
    KeyboardEvent,
    WindowEvent,
    WaitEvent,
    InputRecorder
)

# 获取日志记录器
logger = get_logger(__name__)

# 设置pyautogui安全选项
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class InputPlayer:
    """输入事件回放器"""
    
    def __init__(self):
        """初始化回放器"""
        self.events: List[InputEvent] = []
        self.playing = False
        self.paused = False
        self.speed = 1.0  # 回放速度倍率
        
        # 线程
        self.play_thread = None
        
        # 回调函数
        self.on_event_callback = None
        self.on_complete_callback = None
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 事件索引
        self.current_index = 0
        
        # 录制器，用于加载录制文件
        self.recorder = InputRecorder()
        
        logger.debug("输入回放器已初始化")
    
    def load_events(self, events: List[InputEvent]) -> None:
        """
        加载事件列表
        
        参数:
            events: 事件列表
        """
        with self.lock:
            self.events = events.copy()
            self.current_index = 0
        
        logger.debug(f"已加载 {len(events)} 个事件")
    
    def load_recording(self, file_path: str) -> bool:
        """
        加载录制文件
        
        参数:
            file_path: 文件路径
        
        返回:
            bool: 是否成功加载
        """
        events = self.recorder.load_recording(file_path)
        if events:
            self.load_events(events)
            return True
        return False
    
    def start_playback(
        self,
        on_event: Optional[Callable[[InputEvent, int], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        speed: float = 1.0
    ) -> bool:
        """
        开始回放
        
        参数:
            on_event: 事件回调函数，当回放事件时调用
            on_complete: 完成回调函数，当回放完成时调用
            speed: 回放速度倍率
        
        返回:
            bool: 是否成功开始回放
        """
        if self.playing:
            logger.warning("回放已经在进行中")
            return False
        
        if not self.events:
            logger.warning("没有可回放的事件")
            return False
        
        try:
            with self.lock:
                self.playing = True
                self.paused = False
                self.current_index = 0
                self.on_event_callback = on_event
                self.on_complete_callback = on_complete
                self.speed = max(0.1, min(10.0, speed))  # 限制速度在0.1-10倍之间
            
            # 创建回放线程
            self.play_thread = threading.Thread(target=self._playback_thread)
            self.play_thread.daemon = True
            self.play_thread.start()
            
            logger.info(f"开始回放，共 {len(self.events)} 个事件，速度: {self.speed}x")
            return True
        
        except Exception as e:
            logger.error(f"开始回放失败: {str(e)}")
            self.playing = False
            return False
    
    def stop_playback(self) -> None:
        """停止回放"""
        if not self.playing:
            return
        
        with self.lock:
            self.playing = False
            self.paused = False
        
        logger.info("停止回放")
    
    def pause_playback(self) -> None:
        """暂停回放"""
        if not self.playing or self.paused:
            return
        
        with self.lock:
            self.paused = True
        
        logger.info("暂停回放")
    
    def resume_playback(self) -> None:
        """恢复回放"""
        if not self.playing or not self.paused:
            return
        
        with self.lock:
            self.paused = False
        
        logger.info("恢复回放")
    
    def set_speed(self, speed: float) -> None:
        """
        设置回放速度
        
        参数:
            speed: 速度倍率
        """
        with self.lock:
            self.speed = max(0.1, min(10.0, speed))
        
        logger.debug(f"设置回放速度: {self.speed}x")
    
    def _playback_thread(self) -> None:
        """回放线程"""
        try:
            start_time = time.time()
            last_event_time = start_time
            
            while self.playing and self.current_index < len(self.events):
                # 检查是否暂停
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # 获取当前事件
                with self.lock:
                    if self.current_index >= len(self.events):
                        break
                    
                    event = self.events[self.current_index]
                    current_index = self.current_index
                
                # 调用事件回调
                if self.on_event_callback:
                    self.on_event_callback(event, current_index)
                
                # 处理事件
                self._play_event(event)
                
                # 更新索引
                with self.lock:
                    self.current_index += 1
                
                # 检查是否是最后一个事件
                if self.current_index >= len(self.events):
                    break
                
                # 获取下一个事件
                with self.lock:
                    if self.current_index >= len(self.events):
                        break
                    
                    next_event = self.events[self.current_index]
                
                # 计算等待时间
                if next_event.timestamp > event.timestamp:
                    wait_time = (next_event.timestamp - event.timestamp) / self.speed
                    time.sleep(max(0, wait_time))
            
            # 回放完成
            with self.lock:
                self.playing = False
                self.paused = False
            
            # 调用完成回调
            if self.on_complete_callback:
                self.on_complete_callback()
            
            logger.info("回放完成")
        
        except Exception as e:
            logger.error(f"回放线程异常: {str(e)}")
            
            with self.lock:
                self.playing = False
                self.paused = False
    
    def _play_event(self, event: InputEvent) -> None:
        """
        回放单个事件
        
        参数:
            event: 输入事件
        """
        try:
            # 根据事件类型处理
            if isinstance(event, MouseEvent):
                self._play_mouse_event(event)
            elif isinstance(event, KeyboardEvent):
                self._play_keyboard_event(event)
            elif isinstance(event, WindowEvent):
                self._play_window_event(event)
            elif isinstance(event, WaitEvent):
                self._play_wait_event(event)
            else:
                logger.warning(f"未知事件类型: {event.event_type}")
        
        except Exception as e:
            logger.error(f"回放事件失败: {str(e)}")
    
    def _play_mouse_event(self, event: MouseEvent) -> None:
        """
        回放鼠标事件
        
        参数:
            event: 鼠标事件
        """
        try:
            # 根据事件类型处理
            if event.event_type == "mouse_move":
                pyautogui.moveTo(event.x, event.y)
                logger.debug(f"鼠标移动到 ({event.x}, {event.y})")
            
            elif event.event_type == "mouse_click":
                if event.button == "left":
                    pyautogui.click(event.x, event.y, button="left")
                    logger.debug(f"鼠标左键点击 ({event.x}, {event.y})")
                elif event.button == "right":
                    pyautogui.click(event.x, event.y, button="right")
                    logger.debug(f"鼠标右键点击 ({event.x}, {event.y})")
                elif event.button == "middle":
                    pyautogui.click(event.x, event.y, button="middle")
                    logger.debug(f"鼠标中键点击 ({event.x}, {event.y})")
            
            elif event.event_type == "mouse_right_click":
                pyautogui.click(event.x, event.y, button="right")
                logger.debug(f"鼠标右键点击 ({event.x}, {event.y})")
            
            elif event.event_type == "mouse_wheel":
                if event.wheel_delta:
                    pyautogui.scroll(event.wheel_delta * 10)  # 滚动量需要调整
                    logger.debug(f"鼠标滚轮滚动 {event.wheel_delta}")
        
        except Exception as e:
            logger.error(f"回放鼠标事件失败: {str(e)}")
    
    def _play_keyboard_event(self, event: KeyboardEvent) -> None:
        """
        回放键盘事件
        
        参数:
            event: 键盘事件
        """
        try:
            # 处理特殊按键
            key = event.key
            if key == "space":
                key = " "
            elif key == "enter":
                key = "\n"
            
            # 根据事件类型处理
            if event.event_type == "keyboard_press":
                # 处理修饰键
                if event.modifiers:
                    # 按下修饰键
                    for modifier in event.modifiers:
                        keyboard.press(modifier)
                    
                    # 按下主键
                    keyboard.press(key)
                    
                    # 释放修饰键
                    for modifier in reversed(event.modifiers):
                        keyboard.release(modifier)
                else:
                    # 直接按下按键
                    keyboard.press(key)
                
                logger.debug(f"键盘按下 {key}")
            
            elif event.event_type == "keyboard_release":
                keyboard.release(key)
                logger.debug(f"键盘释放 {key}")
        
        except Exception as e:
            logger.error(f"回放键盘事件失败: {str(e)}")
    
    def _play_window_event(self, event: WindowEvent) -> None:
        """
        回放窗口事件
        
        参数:
            event: 窗口事件
        """
        try:
            # 根据事件类型处理
            if event.event_type == "window_activate":
                # 查找窗口
                hwnd = win32gui.FindWindow(None, event.window_title)
                if hwnd:
                    # 激活窗口
                    win32gui.SetForegroundWindow(hwnd)
                    logger.debug(f"激活窗口: {event.window_title}")
                else:
                    logger.warning(f"找不到窗口: {event.window_title}")
        
        except Exception as e:
            logger.error(f"回放窗口事件失败: {str(e)}")
    
    def _play_wait_event(self, event: WaitEvent) -> None:
        """
        回放等待事件
        
        参数:
            event: 等待事件
        """
        try:
            # 计算等待时间
            wait_time = event.duration / self.speed
            
            # 等待
            time.sleep(wait_time)
            
            logger.debug(f"等待 {wait_time:.2f} 秒")
        
        except Exception as e:
            logger.error(f"回放等待事件失败: {str(e)}")


"""
使用示例：

from core.player import InputPlayer
from core.recorder import InputRecorder

# 创建录制器和回放器
recorder = InputRecorder()
player = InputPlayer()

# 录制一些事件
recorder.start_recording()
# ... 用户操作 ...
events = recorder.stop_recording()

# 保存录制结果
recorder.save_recording("recording.json")

# 加载录制结果
player.load_recording("recording.json")

# 回放事件
def on_event(event, index):
    print(f"回放事件 {index}: {event.event_type}")

def on_complete():
    print("回放完成")

player.start_playback(on_event, on_complete, speed=1.5)

# 等待回放完成
import time
while player.playing:
    time.sleep(0.1)
"""
"""
输入事件录制模块
提供鼠标和键盘事件的录制功能
"""

import os
import time
import json
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime

# 用于捕获输入事件的库
import keyboard
import mouse
from pynput import mouse as pynput_mouse
from pynput import keyboard as pynput_keyboard

# 导入项目模块
from logger import get_logger
from config import config

# 获取日志记录器
logger = get_logger(__name__)

class InputEvent:
    """输入事件基类"""
    
    def __init__(self, event_type: str, timestamp: float):
        """
        初始化输入事件
        
        参数:
            event_type: 事件类型
            timestamp: 事件时间戳
        """
        self.event_type = event_type
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 事件字典
        """
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputEvent':
        """
        从字典创建事件
        
        参数:
            data: 事件字典
        
        返回:
            InputEvent: 输入事件对象
        """
        return cls(data["event_type"], data["timestamp"])


class MouseEvent(InputEvent):
    """鼠标事件"""
    
    def __init__(
        self,
        event_type: str,
        timestamp: float,
        x: int,
        y: int,
        button: Optional[str] = None,
        wheel_delta: Optional[int] = None
    ):
        """
        初始化鼠标事件
        
        参数:
            event_type: 事件类型 (move, click, double_click, right_click, wheel)
            timestamp: 事件时间戳
            x: 鼠标X坐标
            y: 鼠标Y坐标
            button: 鼠标按钮 (left, right, middle)
            wheel_delta: 滚轮增量
        """
        super().__init__(f"mouse_{event_type}", timestamp)
        self.x = x
        self.y = y
        self.button = button
        self.wheel_delta = wheel_delta
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 事件字典
        """
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y
        })
        
        if self.button:
            data["button"] = self.button
        
        if self.wheel_delta is not None:
            data["wheel_delta"] = self.wheel_delta
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseEvent':
        """
        从字典创建事件
        
        参数:
            data: 事件字典
        
        返回:
            MouseEvent: 鼠标事件对象
        """
        return cls(
            data["event_type"].replace("mouse_", ""),
            data["timestamp"],
            data["x"],
            data["y"],
            data.get("button"),
            data.get("wheel_delta")
        )


class KeyboardEvent(InputEvent):
    """键盘事件"""
    
    def __init__(
        self,
        event_type: str,
        timestamp: float,
        key: str,
        modifiers: Optional[List[str]] = None
    ):
        """
        初始化键盘事件
        
        参数:
            event_type: 事件类型 (press, release)
            timestamp: 事件时间戳
            key: 按键名称
            modifiers: 修饰键列表 (ctrl, alt, shift, win)
        """
        super().__init__(f"keyboard_{event_type}", timestamp)
        self.key = key
        self.modifiers = modifiers or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 事件字典
        """
        data = super().to_dict()
        data.update({
            "key": self.key,
            "modifiers": self.modifiers
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardEvent':
        """
        从字典创建事件
        
        参数:
            data: 事件字典
        
        返回:
            KeyboardEvent: 键盘事件对象
        """
        return cls(
            data["event_type"].replace("keyboard_", ""),
            data["timestamp"],
            data["key"],
            data.get("modifiers", [])
        )


class WindowEvent(InputEvent):
    """窗口事件"""
    
    def __init__(
        self,
        event_type: str,
        timestamp: float,
        window_title: str,
        window_class: Optional[str] = None
    ):
        """
        初始化窗口事件
        
        参数:
            event_type: 事件类型 (activate, close)
            timestamp: 事件时间戳
            window_title: 窗口标题
            window_class: 窗口类名
        """
        super().__init__(f"window_{event_type}", timestamp)
        self.window_title = window_title
        self.window_class = window_class
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 事件字典
        """
        data = super().to_dict()
        data.update({
            "window_title": self.window_title
        })
        
        if self.window_class:
            data["window_class"] = self.window_class
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowEvent':
        """
        从字典创建事件
        
        参数:
            data: 事件字典
        
        返回:
            WindowEvent: 窗口事件对象
        """
        return cls(
            data["event_type"].replace("window_", ""),
            data["timestamp"],
            data["window_title"],
            data.get("window_class")
        )


class WaitEvent(InputEvent):
    """等待事件"""
    
    def __init__(self, timestamp: float, duration: float):
        """
        初始化等待事件
        
        参数:
            timestamp: 事件时间戳
            duration: 等待时间（秒）
        """
        super().__init__("wait", timestamp)
        self.duration = duration
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 事件字典
        """
        data = super().to_dict()
        data.update({
            "duration": self.duration
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaitEvent':
        """
        从字典创建事件
        
        参数:
            data: 事件字典
        
        返回:
            WaitEvent: 等待事件对象
        """
        return cls(data["timestamp"], data["duration"])


class InputRecorder:
    """输入事件录制器"""
    
    def __init__(self):
        """初始化录制器"""
        self.events: List[InputEvent] = []
        self.recording = False
        self.start_time = 0.0
        self.last_event_time = 0.0
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 鼠标监听器
        self.mouse_listener = None
        
        # 键盘监听器
        self.keyboard_listener = None
        
        # 回调函数
        self.on_event_callback = None
        
        logger.debug("输入录制器已初始化")
    
    def start_recording(self, on_event: Optional[Callable[[InputEvent], None]] = None) -> bool:
        """
        开始录制
        
        参数:
            on_event: 事件回调函数，当有新事件时调用
        
        返回:
            bool: 是否成功开始录制
        """
        if self.recording:
            logger.warning("录制已经在进行中")
            return False
        
        try:
            with self.lock:
                self.events = []
                self.recording = True
                self.start_time = time.time()
                self.last_event_time = self.start_time
                self.on_event_callback = on_event
            
            # 创建鼠标监听器
            self.mouse_listener = pynput_mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            
            # 创建键盘监听器
            self.keyboard_listener = pynput_keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            # 启动监听器
            self.mouse_listener.start()
            self.keyboard_listener.start()
            
            logger.info("开始录制输入事件")
            return True
        
        except Exception as e:
            logger.error(f"开始录制失败: {str(e)}")
            self.recording = False
            return False
    
    def stop_recording(self) -> List[InputEvent]:
        """
        停止录制
        
        返回:
            List[InputEvent]: 录制的事件列表
        """
        if not self.recording:
            logger.warning("没有正在进行的录制")
            return self.events
        
        try:
            # 停止监听器
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            
            with self.lock:
                self.recording = False
                events_copy = self.events.copy()
            
            logger.info(f"停止录制，共记录 {len(events_copy)} 个事件")
            return events_copy
        
        except Exception as e:
            logger.error(f"停止录制失败: {str(e)}")
            self.recording = False
            return self.events
    
    def save_recording(self, file_path: str) -> bool:
        """
        保存录制结果
        
        参数:
            file_path: 保存路径
        
        返回:
            bool: 是否成功保存
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 转换事件为字典列表
            events_data = []
            with self.lock:
                for event in self.events:
                    events_data.append(event.to_dict())
            
            # 创建录制数据
            recording_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "events_count": len(events_data),
                "events": events_data
            }
            
            # 保存为JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recording_data, f, indent=2)
            
            logger.info(f"已保存录制结果: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"保存录制结果失败: {str(e)}")
            return False
    
    def load_recording(self, file_path: str) -> List[InputEvent]:
        """
        加载录制结果
        
        参数:
            file_path: 文件路径
        
        返回:
            List[InputEvent]: 加载的事件列表
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"录制文件不存在: {file_path}")
                return []
            
            # 加载JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                recording_data = json.load(f)
            
            # 检查版本
            version = recording_data.get("version", "1.0")
            if version != "1.0":
                logger.warning(f"录制文件版本不匹配: {version}")
            
            # 转换事件
            events = []
            for event_data in recording_data.get("events", []):
                event_type = event_data.get("event_type", "")
                
                if event_type.startswith("mouse_"):
                    event = MouseEvent.from_dict(event_data)
                elif event_type.startswith("keyboard_"):
                    event = KeyboardEvent.from_dict(event_data)
                elif event_type.startswith("window_"):
                    event = WindowEvent.from_dict(event_data)
                elif event_type == "wait":
                    event = WaitEvent.from_dict(event_data)
                else:
                    logger.warning(f"未知事件类型: {event_type}")
                    continue
                
                events.append(event)
            
            logger.info(f"已加载录制结果: {file_path}，共 {len(events)} 个事件")
            
            with self.lock:
                self.events = events
            
            return events
        
        except Exception as e:
            logger.error(f"加载录制结果失败: {str(e)}")
            return []
    
    def add_event(self, event: InputEvent) -> None:
        """
        添加事件
        
        参数:
            event: 输入事件
        """
        if not self.recording:
            return
        
        with self.lock:
            # 添加等待事件
            if self.events and config.get("recording.add_waits", True):
                wait_time = event.timestamp - self.last_event_time
                if wait_time > 0.1:  # 只添加大于100毫秒的等待
                    wait_event = WaitEvent(self.last_event_time, wait_time)
                    self.events.append(wait_event)
                    
                    # 调用回调函数
                    if self.on_event_callback:
                        self.on_event_callback(wait_event)
            
            # 添加事件
            self.events.append(event)
            self.last_event_time = event.timestamp
            
            # 调用回调函数
            if self.on_event_callback:
                self.on_event_callback(event)
    
    def _on_mouse_move(self, x, y) -> None:
        """
        鼠标移动事件处理
        
        参数:
            x: X坐标
            y: Y坐标
        """
        # 如果配置不记录鼠标移动，则跳过
        if not config.get("recording.record_mouse_move", True):
            return
        
        # 如果配置了移动阈值，则检查移动距离
        threshold = config.get("recording.mouse_move_threshold", 5)
        if threshold > 0 and self.events:
            # 查找最后一个鼠标移动事件
            last_move = None
            for event in reversed(self.events):
                if event.event_type == "mouse_move":
                    last_move = event
                    break
            
            # 如果找到了最后一个移动事件，检查移动距离
            if last_move:
                dx = abs(x - last_move.x)
                dy = abs(y - last_move.y)
                if dx < threshold and dy < threshold:
                    return
        
        # 创建鼠标移动事件
        event = MouseEvent("move", time.time(), x, y)
        self.add_event(event)
    
    def _on_mouse_click(self, x, y, button, pressed) -> None:
        """
        鼠标点击事件处理
        
        参数:
            x: X坐标
            y: Y坐标
            button: 按钮
            pressed: 是否按下
        """
        # 转换按钮名称
        button_name = str(button).split(".")[-1].lower()
        
        # 创建鼠标事件
        if pressed:
            event_type = "click"
            if button_name == "right":
                event_type = "right_click"
        else:
            event_type = "release"
        
        event = MouseEvent(event_type, time.time(), x, y, button_name)
        self.add_event(event)
    
    def _on_mouse_scroll(self, x, y, dx, dy) -> None:
        """
        鼠标滚轮事件处理
        
        参数:
            x: X坐标
            y: Y坐标
            dx: 水平滚动
            dy: 垂直滚动
        """
        # 创建鼠标滚轮事件
        event = MouseEvent("wheel", time.time(), x, y, wheel_delta=int(dy))
        self.add_event(event)
    
    def _on_key_press(self, key) -> None:
        """
        键盘按下事件处理
        
        参数:
            key: 按键
        """
        try:
            # 获取按键名称
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            else:
                key_name = str(key).split(".")[-1].lower()
                if key_name.startswith("'") and key_name.endswith("'"):
                    key_name = key_name[1:-1]
            
            # 获取修饰键
            modifiers = []
            if keyboard.is_pressed('ctrl'):
                modifiers.append('ctrl')
            if keyboard.is_pressed('alt'):
                modifiers.append('alt')
            if keyboard.is_pressed('shift'):
                modifiers.append('shift')
            if keyboard.is_pressed('win'):
                modifiers.append('win')
            
            # 创建键盘事件
            event = KeyboardEvent("press", time.time(), key_name, modifiers)
            self.add_event(event)
        
        except Exception as e:
            logger.error(f"处理键盘按下事件失败: {str(e)}")
    
    def _on_key_release(self, key) -> None:
        """
        键盘释放事件处理
        
        参数:
            key: 按键
        """
        try:
            # 获取按键名称
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            else:
                key_name = str(key).split(".")[-1].lower()
                if key_name.startswith("'") and key_name.endswith("'"):
                    key_name = key_name[1:-1]
            
            # 创建键盘事件
            event = KeyboardEvent("release", time.time(), key_name)
            self.add_event(event)
        
        except Exception as e:
            logger.error(f"处理键盘释放事件失败: {str(e)}")


"""
使用示例：

from core.recorder import InputRecorder

# 创建录制器
recorder = InputRecorder()

# 开始录制
recorder.start_recording()

# 等待一段时间...
import time
time.sleep(10)

# 停止录制
events = recorder.stop_recording()

# 保存录制结果
recorder.save_recording("recording.json")

# 加载录制结果
events = recorder.load_recording("recording.json")

# 打印事件
for event in events:
    print(event.to_dict())
"""
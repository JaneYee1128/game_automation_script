"""
屏幕捕获模块
提供屏幕截图和窗口捕获功能
"""

import os
import time
import logging
from typing import Optional, Tuple, Union, List
from PIL import Image, ImageGrab
import numpy as np

from config import config

logger = logging.getLogger('ScreenCapture')

# 尝试导入mss库，用于更高效的屏幕捕获
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logger.warning("未安装mss库，将使用PIL进行屏幕捕获")

# 尝试导入win32gui库，用于Windows窗口捕获
try:
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("未安装pywin32库，窗口捕获功能将不可用")


class ScreenCapture:
    """屏幕捕获类，提供屏幕截图和窗口捕获功能"""
    
    def __init__(self):
        """初始化屏幕捕获"""
        self.use_mss = MSS_AVAILABLE and config.get('capture.use_mss', True)
        self.debug_mode = config.get('capture.debug_mode', False)
        
        # 如果使用mss，初始化mss对象
        if self.use_mss:
            self.mss = mss.mss()
    
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        捕获屏幕截图
        
        参数:
            region: 捕获区域 (x, y, width, height)，None则捕获整个屏幕
        
        返回:
            PIL图像对象
        """
        try:
            if self.use_mss:
                return self._capture_with_mss(region)
            else:
                return self._capture_with_pil(region)
        except Exception as e:
            logger.error(f"屏幕捕获失败: {str(e)}")
            # 返回一个空白图像
            return Image.new('RGB', (800, 600), color='black')
    
    def _capture_with_mss(self, region: Optional[Tuple[int, int, int, int]]) -> Image.Image:
        """使用mss库捕获屏幕"""
        if region:
            x, y, w, h = region
            monitor = {"top": y, "left": x, "width": w, "height": h}
        else:
            monitor = self.mss.monitors[0]  # 主显示器
        
        screenshot = self.mss.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # 调试模式：保存截图
        if self.debug_mode:
            self._save_debug_image(img, 'mss_capture')
        
        return img
    
    def _capture_with_pil(self, region: Optional[Tuple[int, int, int, int]]) -> Image.Image:
        """使用PIL库捕获屏幕"""
        if region:
            x, y, w, h = region
            screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        else:
            screenshot = ImageGrab.grab()
        
        # 调试模式：保存截图
        if self.debug_mode:
            self._save_debug_image(screenshot, 'pil_capture')
        
        return screenshot
    
    def capture_window(self, window_title: str) -> Optional[Image.Image]:
        """
        捕获指定窗口的截图
        
        参数:
            window_title: 窗口标题
        
        返回:
            成功则返回PIL图像对象，失败则返回None
        """
        if not WIN32_AVAILABLE:
            logger.error("未安装pywin32库，无法使用窗口捕获功能")
            return None
        
        try:
            # 查找窗口句柄
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                logger.error(f"未找到窗口: {window_title}")
                return None
            
            # 获取窗口大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # 复制窗口内容到位图
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            
            # 转换为PIL图像
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            # 清理资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            # 调试模式：保存截图
            if self.debug_mode:
                self._save_debug_image(img, 'window_capture')
            
            return img
        except Exception as e:
            logger.error(f"窗口捕获失败: {str(e)}")
            return None
    
    def get_window_position(self, window_title: str) -> Optional[Tuple[int, int, int, int]]:
        """
        获取窗口位置和大小
        
        参数:
            window_title: 窗口标题
        
        返回:
            成功则返回窗口位置和大小 (x, y, width, height)，失败则返回None
        """
        if not WIN32_AVAILABLE:
            logger.error("未安装pywin32库，无法获取窗口位置")
            return None
        
        try:
            # 查找窗口句柄
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                logger.error(f"未找到窗口: {window_title}")
                return None
            
            # 获取窗口大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            return (left, top, width, height)
        except Exception as e:
            logger.error(f"获取窗口位置失败: {str(e)}")
            return None
    
    def list_windows(self) -> List[str]:
        """
        列出所有可见窗口
        
        返回:
            窗口标题列表
        """
        if not WIN32_AVAILABLE:
            logger.error("未安装pywin32库，无法列出窗口")
            return []
        
        try:
            windows = []
            
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:
                        results.append(window_title)
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows
        except Exception as e:
            logger.error(f"列出窗口失败: {str(e)}")
            return []
    
    def _save_debug_image(self, image: Image.Image, prefix: str) -> None:
        """
        保存调试图像
        
        参数:
            image: 图像对象
            prefix: 文件名前缀
        """
        try:
            # 创建调试图像目录
            debug_dir = os.path.join(config.get('paths.debug', 'debug'), 'screen_capture')
            os.makedirs(debug_dir, exist_ok=True)
            
            # 保存图像
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"{prefix}_{timestamp}.png"
            filepath = os.path.join(debug_dir, filename)
            
            image.save(filepath)
            logger.debug(f"保存调试图像: {filepath}")
        except Exception as e:
            logger.error(f"保存调试图像失败: {str(e)}")

"""
使用示例：

# 创建屏幕捕获实例
capture = ScreenCapture()

# 捕获整个屏幕
screenshot = capture.capture()
screenshot.save("full_screen.png")

# 捕获指定区域
region = (100, 100, 400, 300)  # x, y, width, height
region_screenshot = capture.capture(region)
region_screenshot.save("region.png")

# 捕获指定窗口
window_screenshot = capture.capture_window("记事本")
if window_screenshot:
    window_screenshot.save("notepad.png")

# 获取窗口位置
window_pos = capture.get_window_position("记事本")
if window_pos:
    print(f"窗口位置: {window_pos}")

# 列出所有窗口
windows = capture.list_windows()
print("可见窗口:")
for window in windows:
    print(f"- {window}")
"""
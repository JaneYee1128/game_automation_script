"""
屏幕截图和窗口捕获模块
提供屏幕截图、窗口捕获和图像处理功能
"""

import os
import time
import logging
from typing import List, Optional, Tuple, Dict, Any, Union

import cv2
import numpy as np
from PIL import Image, ImageGrab
import pytesseract

# Windows平台特定导入
import ctypes
from ctypes import wintypes
import win32gui
import win32ui
import win32con
import win32api

# 导入项目模块
from logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class ScreenCapture:
    """屏幕截图和窗口捕获类"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        初始化截图类
        
        参数:
            tesseract_path: Tesseract OCR可执行文件路径，用于文本识别
        """
        self.tesseract_path = tesseract_path
        
        # 如果提供了Tesseract路径，则设置pytesseract配置
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        logger.debug("屏幕截图模块已初始化")
    
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        捕获屏幕截图
        
        参数:
            region: 截图区域 (left, top, right, bottom)，如果为None则截取整个屏幕
        
        返回:
            Image.Image: PIL图像对象
        """
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            logger.debug(f"已捕获屏幕截图，区域: {region if region else '全屏'}")
            return screenshot
        
        except Exception as e:
            logger.error(f"捕获屏幕截图失败: {str(e)}")
            raise
    
    def capture_window(self, window_title: str) -> Optional[Image.Image]:
        """
        捕获指定窗口的截图
        
        参数:
            window_title: 窗口标题
        
        返回:
            Optional[Image.Image]: 窗口截图，如果找不到窗口则返回None
        """
        try:
            # 查找窗口句柄
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                logger.warning(f"找不到窗口: {window_title}")
                return None
            
            # 获取窗口大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # 获取窗口DC
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # 创建位图对象
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            # 复制窗口内容到位图
            result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)
            
            # 转换为PIL图像
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # 清理资源
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            
            logger.debug(f"已捕获窗口截图: {window_title}")
            return img
        
        except Exception as e:
            logger.error(f"捕获窗口截图失败: {str(e)}")
            return None
    
    def list_windows(self) -> List[str]:
        """
        列出所有可见窗口
        
        返回:
            List[str]: 窗口标题列表
        """
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    windows.append(window_text)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        logger.debug(f"找到 {len(windows)} 个可见窗口")
        return windows
    
    def find_image(
        self,
        template_path: str,
        screenshot: Optional[Image.Image] = None,
        threshold: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None,
        max_wait: float = 0.0
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        在屏幕上查找图像
        
        参数:
            template_path: 模板图像路径
            screenshot: 截图，如果为None则自动截图
            threshold: 匹配阈值，0-1之间，越高要求越精确
            region: 搜索区域 (left, top, right, bottom)
            max_wait: 最大等待时间（秒），如果大于0则会不断尝试直到找到或超时
        
        返回:
            Optional[Tuple[int, int, int, int]]: 找到的区域 (left, top, right, bottom)，如果未找到则返回None
        """
        if not os.path.exists(template_path):
            logger.error(f"模板图像不存在: {template_path}")
            return None
        
        # 加载模板图像
        template = cv2.imread(template_path)
        if template is None:
            logger.error(f"无法加载模板图像: {template_path}")
            return None
        
        template_height, template_width = template.shape[:2]
        
        start_time = time.time()
        while True:
            # 获取截图
            if screenshot is None:
                screenshot = self.capture(region)
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 执行模板匹配
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 检查是否匹配
            if max_val >= threshold:
                # 计算匹配区域
                left = max_loc[0]
                top = max_loc[1]
                right = left + template_width
                bottom = top + template_height
                
                # 如果指定了区域，需要调整坐标
                if region:
                    left += region[0]
                    top += region[1]
                    right += region[0]
                    bottom += region[1]
                
                logger.debug(f"找到图像 {template_path}，位置: ({left}, {top}, {right}, {bottom})，匹配度: {max_val:.2f}")
                return (left, top, right, bottom)
            
            # 检查是否超时
            if max_wait <= 0 or (time.time() - start_time) > max_wait:
                logger.debug(f"未找到图像 {template_path}，最佳匹配度: {max_val:.2f}")
                return None
            
            # 等待一段时间后重试
            time.sleep(0.1)
            screenshot = None  # 重新截图
    
    def find_text(
        self,
        text: str,
        screenshot: Optional[Image.Image] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        lang: str = 'eng',
        max_wait: float = 0.0
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        在屏幕上查找文本
        
        参数:
            text: 要查找的文本
            screenshot: 截图，如果为None则自动截图
            region: 搜索区域 (left, top, right, bottom)
            lang: OCR语言，默认为英语
            max_wait: 最大等待时间（秒），如果大于0则会不断尝试直到找到或超时
        
        返回:
            Optional[Tuple[int, int, int, int]]: 找到的区域 (left, top, right, bottom)，如果未找到则返回None
        """
        if not self.tesseract_path:
            logger.error("未设置Tesseract路径，无法执行文本识别")
            return None
        
        start_time = time.time()
        while True:
            # 获取截图
            if screenshot is None:
                screenshot = self.capture(region)
            
            # 执行OCR
            try:
                ocr_result = pytesseract.image_to_data(
                    screenshot,
                    lang=lang,
                    output_type=pytesseract.Output.DICT
                )
                
                # 查找文本
                for i, word in enumerate(ocr_result['text']):
                    if text.lower() in word.lower():
                        # 获取文本区域
                        left = ocr_result['left'][i]
                        top = ocr_result['top'][i]
                        width = ocr_result['width'][i]
                        height = ocr_result['height'][i]
                        
                        # 如果指定了区域，需要调整坐标
                        if region:
                            left += region[0]
                            top += region[1]
                        
                        right = left + width
                        bottom = top + height
                        
                        logger.debug(f"找到文本 '{text}'，位置: ({left}, {top}, {right}, {bottom})")
                        return (left, top, right, bottom)
                
            except Exception as e:
                logger.error(f"文本识别失败: {str(e)}")
            
            # 检查是否超时
            if max_wait <= 0 or (time.time() - start_time) > max_wait:
                logger.debug(f"未找到文本 '{text}'")
                return None
            
            # 等待一段时间后重试
            time.sleep(0.1)
            screenshot = None  # 重新截图
    
    def save_screenshot(self, file_path: str, screenshot: Optional[Image.Image] = None) -> bool:
        """
        保存截图
        
        参数:
            file_path: 保存路径
            screenshot: 截图，如果为None则自动截图
        
        返回:
            bool: 是否成功保存
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 获取截图
            if screenshot is None:
                screenshot = self.capture()
            
            # 保存截图
            screenshot.save(file_path)
            
            logger.debug(f"已保存截图: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"保存截图失败: {str(e)}")
            return False

"""
使用示例：

from core.capture import ScreenCapture

# 创建截图对象
capture = ScreenCapture()

# 捕获全屏截图
screenshot = capture.capture()

# 捕获指定区域截图
region_screenshot = capture.capture((100, 100, 500, 500))

# 捕获指定窗口截图
window_screenshot = capture.capture_window("记事本")

# 列出所有可见窗口
windows = capture.list_windows()
for window in windows:
    print(window)

# 查找图像
result = capture.find_image("template.png", threshold=0.9)
if result:
    left, top, right, bottom = result
    print(f"找到图像，位置: ({left}, {top}, {right}, {bottom})")

# 查找文本（需要设置Tesseract路径）
capture = ScreenCapture(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
result = capture.find_text("Hello World")
if result:
    left, top, right, bottom = result
    print(f"找到文本，位置: ({left}, {top}, {right}, {bottom})")

# 保存截图
capture.save_screenshot("screenshot.png")
"""
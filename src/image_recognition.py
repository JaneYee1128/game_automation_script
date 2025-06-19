"""
图像识别模块
提供图像模板匹配和文字识别功能
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Optional, Tuple, List, Union

from config import config

logger = logging.getLogger('ImageRecognition')

class ImageRecognition:
    """图像识别类，提供图像模板匹配和文字识别功能"""
    
    def __init__(self):
        """初始化图像识别"""
        # 设置Tesseract OCR路径
        if hasattr(config, 'tesseract_path') and config.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_path
        
        # 设置默认参数
        self.match_threshold = config.get('recognition.match_threshold', 0.8)
        self.ocr_lang = config.get('recognition.ocr_language', 'eng')
        self.debug_mode = config.get('recognition.debug_mode', False)
    
    def find_template(self, 
                     image: Union[str, np.ndarray, Image.Image],
                     template: Union[str, np.ndarray, Image.Image],
                     confidence: float = None,
                     region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        在图像中查找模板图像
        
        参数:
            image: 要搜索的图像（文件路径、numpy数组或PIL图像）
            template: 要查找的模板图像（文件路径、numpy数组或PIL图像）
            confidence: 匹配阈值（0-1），None则使用默认值
            region: 搜索区域 (x, y, width, height)，None则搜索整个图像
        
        返回:
            成功则返回匹配区域 (x, y, width, height)，失败则返回None
        """
        try:
            # 加载图像
            img = self._load_image(image)
            if region:
                x, y, w, h = region
                img = img[y:y+h, x:x+w]
            
            # 加载模板
            tpl = self._load_image(template)
            
            # 确保图像大小合适
            if tpl.shape[0] > img.shape[0] or tpl.shape[1] > img.shape[1]:
                logger.error("模板图像大于搜索图像")
                return None
            
            # 设置匹配阈值
            if confidence is None:
                confidence = self.match_threshold
            
            # 执行模板匹配
            result = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # 计算匹配区域
                w, h = tpl.shape[1], tpl.shape[0]
                x, y = max_loc
                
                if region:
                    # 如果指定了搜索区域，需要调整返回的坐标
                    x += region[0]
                    y += region[1]
                
                match_region = (x, y, w, h)
                
                # 调试模式：保存匹配结果图像
                if self.debug_mode:
                    self._save_debug_image(img, match_region, 'template_match')
                
                return match_region
            else:
                return None
        except Exception as e:
            logger.error(f"模板匹配失败: {str(e)}")
            return None
    
    def find_text(self,
                  image: Union[str, np.ndarray, Image.Image],
                  text: str,
                  region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        在图像中查找文本
        
        参数:
            image: 要搜索的图像（文件路径、numpy数组或PIL图像）
            text: 要查找的文本
            region: 搜索区域 (x, y, width, height)，None则搜索整个图像
        
        返回:
            成功则返回文本区域 (x, y, width, height)，失败则返回None
        """
        try:
            # 加载图像
            img = self._load_image(image)
            if region:
                x, y, w, h = region
                img = img[y:y+h, x:x+w]
            
            # 转换为PIL图像
            if isinstance(img, np.ndarray):
                img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # 执行OCR
            result = pytesseract.image_to_data(
                img,
                lang=self.ocr_lang,
                output_type=pytesseract.Output.DICT
            )
            
            # 查找匹配的文本
            text = text.lower()
            for i, word in enumerate(result['text']):
                if text in word.lower():
                    # 获取文本区域
                    x = result['left'][i]
                    y = result['top'][i]
                    w = result['width'][i]
                    h = result['height'][i]
                    
                    if region:
                        # 如果指定了搜索区域，需要调整返回的坐标
                        x += region[0]
                        y += region[1]
                    
                    text_region = (x, y, w, h)
                    
                    # 调试模式：保存匹配结果图像
                    if self.debug_mode:
                        self._save_debug_image(img, text_region, 'text_match')
                    
                    return text_region
            
            return None
        except Exception as e:
            logger.error(f"文本识别失败: {str(e)}")
            return None
    
    def get_text(self,
                 image: Union[str, np.ndarray, Image.Image],
                 region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        获取图像中的文本
        
        参数:
            image: 要识别的图像（文件路径、numpy数组或PIL图像）
            region: 识别区域 (x, y, width, height)，None则识别整个图像
        
        返回:
            识别到的文本
        """
        try:
            # 加载图像
            img = self._load_image(image)
            if region:
                x, y, w, h = region
                img = img[y:y+h, x:x+w]
            
            # 转换为PIL图像
            if isinstance(img, np.ndarray):
                img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # 执行OCR
            text = pytesseract.image_to_string(img, lang=self.ocr_lang)
            return text.strip()
        except Exception as e:
            logger.error(f"文本识别失败: {str(e)}")
            return ""
    
    def _load_image(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """
        加载图像
        
        参数:
            image: 图像源（文件路径、numpy数组或PIL图像）
        
        返回:
            numpy数组格式的图像
        """
        if isinstance(image, str):
            # 从文件加载
            return cv2.imread(image)
        elif isinstance(image, np.ndarray):
            # 已经是numpy数组
            return image
        elif isinstance(image, Image.Image):
            # 从PIL图像转换
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            raise ValueError("不支持的图像格式")
    
    def _save_debug_image(self,
                         image: np.ndarray,
                         region: Tuple[int, int, int, int],
                         prefix: str) -> None:
        """
        保存调试图像
        
        参数:
            image: 原始图像
            region: 标记区域 (x, y, width, height)
            prefix: 文件名前缀
        """
        try:
            # 创建调试图像目录
            debug_dir = os.path.join(config.get('paths.debug', 'debug'), 'image_recognition')
            os.makedirs(debug_dir, exist_ok=True)
            
            # 复制图像
            debug_img = image.copy()
            
            # 绘制矩形标记
            x, y, w, h = region
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 保存图像
            import time
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"{prefix}_{timestamp}.png"
            filepath = os.path.join(debug_dir, filename)
            
            cv2.imwrite(filepath, debug_img)
            logger.debug(f"保存调试图像: {filepath}")
        except Exception as e:
            logger.error(f"保存调试图像失败: {str(e)}")

"""
使用示例：

# 创建图像识别实例
recognition = ImageRecognition()

# 在屏幕截图中查找模板图像
screenshot = "screenshot.png"
template = "button.png"
result = recognition.find_template(screenshot, template, confidence=0.9)
if result:
    x, y, w, h = result
    print(f"找到按钮在位置: ({x}, {y})")

# 在图像中查找文本
text_region = recognition.find_text(screenshot, "开始游戏")
if text_region:
    x, y, w, h = text_region
    print(f"找到文本在位置: ({x}, {y})")

# 获取图像区域中的文本
region = (100, 100, 200, 50)  # x, y, width, height
text = recognition.get_text(screenshot, region)
print(f"识别到的文本: {text}")
"""
# API 参考文档

本文档详细说明了游戏自动化脚本工具的各个模块、类和方法。

## 目录

1. [事件录制模块](#事件录制模块)
2. [事件回放模块](#事件回放模块)
3. [图像识别模块](#图像识别模块)
4. [屏幕捕获模块](#屏幕捕获模块)

## 事件录制模块

### EventRecorder 类

负责录制鼠标和键盘事件。

```python
from src.event_recorder import EventRecorder

recorder = EventRecorder()
```

#### 方法

##### `start_recording()`
开始录制鼠标和键盘事件。

参数：无  
返回值：无

##### `stop_recording()`
停止录制并返回录制数据。

参数：无  
返回值：`dict` - 包含录制事件的字典

##### `save_recording(filename: str)`
保存录制数据到文件。

参数：
- `filename` (str): 保存文件的名称

返回值：`bool` - 保存是否成功

##### `load_recording(filename: str)`
加载已保存的录制文件。

参数：
- `filename` (str): 要加载的文件名称

返回值：`dict` - 加载的录制数据

##### `get_recordings_list()`
获取可用的录制文件列表。

参数：无  
返回值：`List[str]` - 录制文件名称列表

## 事件回放模块

### EventPlayer 类

负责回放录制的事件序列。

```python
from src.event_player import EventPlayer

player = EventPlayer()
```

#### 方法

##### `load_recording(filename: str)`
加载录制文件准备回放。

参数：
- `filename` (str): 要加载的录制文件名称

返回值：`bool` - 加载是否成功

##### `start_playback(speed: float = 1.0)`
开始回放加载的录制。

参数：
- `speed` (float, 可选): 回放速度倍率，默认为1.0

返回值：无

##### `pause_playback()`
暂停当前回放。

参数：无  
返回值：无

##### `resume_playback()`
恢复暂停的回放。

参数：无  
返回值：无

##### `stop_playback()`
停止当前回放。

参数：无  
返回值：无

##### `set_playback_speed(speed: float)`
设置回放速度。

参数：
- `speed` (float): 回放速度倍率（0.5-2.0）

返回值：无

## 图像识别模块

### ImageRecognition 类

提供图像识别和分析功能。

```python
from src.image_recognition import ImageRecognition

recognition = ImageRecognition()
```

#### 方法

##### `find_template(image: np.ndarray, template_name: str, threshold: float = 0.8)`
在图像中查找模板。

参数：
- `image` (np.ndarray): 要搜索的图像
- `template_name` (str): 模板名称
- `threshold` (float, 可选): 匹配阈值，默认为0.8

返回值：`List[Tuple[int, int, int, int, float]]` - 匹配结果列表，每个元素为(x, y, w, h, confidence)

##### `find_text(image: np.ndarray, text: str, lang: str = 'eng')`
使用OCR在图像中查找文字。

参数：
- `image` (np.ndarray): 要搜索的图像
- `text` (str): 要查找的文字
- `lang` (str, 可选): OCR语言，默认为'eng'

返回值：`List[Tuple[int, int, int, int, str]]` - 匹配结果列表，每个元素为(x, y, w, h, text)

##### `compare_images(image1: np.ndarray, image2: np.ndarray)`
比较两个图像的相似度。

参数：
- `image1` (np.ndarray): 第一个图像
- `image2` (np.ndarray): 第二个图像

返回值：`float` - 相似度得分（0-1）

##### `detect_edges(image: np.ndarray)`
检测图像中的边缘。

参数：
- `image` (np.ndarray): 输入图像

返回值：`np.ndarray` - 边缘检测结果图像

##### `detect_circles(image: np.ndarray)`
检测图像中的圆形。

参数：
- `image` (np.ndarray): 输入图像

返回值：`List[Tuple[int, int, int]]` - 圆形列表，每个元素为(x, y, radius)

##### `detect_color(image: np.ndarray, color: Tuple[int, int, int], tolerance: int = 10)`
检测图像中特定颜色的区域。

参数：
- `image` (np.ndarray): 输入图像
- `color` (Tuple[int, int, int]): 目标颜色(R,G,B)
- `tolerance` (int, 可选): 颜色容差，默认为10

返回值：`np.ndarray` - 颜色检测掩码

## 屏幕捕获模块

### ScreenCapture 类

提供屏幕捕获功能。

```python
from src.screen_capture import ScreenCapture

capture = ScreenCapture()
```

#### 方法

##### `capture_screen(region: Optional[Tuple[int, int, int, int]] = None)`
捕获屏幕或指定区域。

参数：
- `region` (Tuple[int, int, int, int], 可选): 捕获区域(x, y, width, height)，默认为None（全屏）

返回值：`np.ndarray` - 捕获的图像

##### `get_pixel_color(x: int, y: int)`
获取指定坐标的像素颜色。

参数：
- `x` (int): X坐标
- `y` (int): Y坐标

返回值：`Tuple[int, int, int]` - RGB颜色值

##### `save_screenshot(filename: str, region: Optional[Tuple[int, int, int, int]] = None)`
保存屏幕截图到文件。

参数：
- `filename` (str): 保存的文件名
- `region` (Tuple[int, int, int, int], 可选): 捕获区域，默认为None（全屏）

返回值：`bool` - 保存是否成功

##### `get_screen_size()`
获取屏幕尺寸。

参数：无  
返回值：`Tuple[int, int]` - (宽度, 高度)

##### `calculate_fps()`
计算当前的帧率。

参数：无  
返回值：`float` - 每秒帧数

## 异常类

### AutomationError

自动化操作的基础异常类。

```python
class AutomationError(Exception):
    pass
```

### RecordingError

录制相关的异常。

```python
class RecordingError(AutomationError):
    pass
```

### PlaybackError

回放相关的异常。

```python
class PlaybackError(AutomationError):
    pass
```

### ImageRecognitionError

图像识别相关的异常。

```python
class ImageRecognitionError(AutomationError):
    pass
```

### ScreenCaptureError

屏幕捕获相关的异常。

```python
class ScreenCaptureError(AutomationError):
    pass
```

## 使用示例

### 基本录制和回放

```python
from src.event_recorder import EventRecorder
from src.event_player import EventPlayer

# 创建录制器和回放器
recorder = EventRecorder()
player = EventPlayer()

# 开始录制
recorder.start_recording()

# ... 执行一些操作 ...

# 停止录制并保存
recorder.stop_recording()
recorder.save_recording("test_recording")

# 加载并回放录制
player.load_recording("test_recording")
player.start_playback(speed=1.5)
```

### 图像识别和屏幕捕获

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition

# 创建屏幕捕获和图像识别对象
capture = ScreenCapture()
recognition = ImageRecognition()

# 捕获屏幕
screen = capture.capture_screen()

# 在屏幕中查找模板
results = recognition.find_template(screen, "button_template")

# 在找到的位置执行点击
if results:
    x, y, w, h, conf = results[0]
    center_x = x + w // 2
    center_y = y + h // 2
    # 使用pyautogui或其他方法点击
```

### 错误处理

```python
from src.automation_errors import AutomationError, RecordingError

try:
    recorder = EventRecorder()
    recorder.start_recording()
    # ... 执行操作 ...
    recorder.stop_recording()
except RecordingError as e:
    print(f"录制错误: {e}")
except AutomationError as e:
    print(f"自动化错误: {e}")
```
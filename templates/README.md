# 模板图像目录

此目录用于存储用于图像识别的模板图像文件。

模板图像是游戏自动化脚本工具用于在屏幕上查找特定元素的参考图像。

## 文件格式

支持的图像格式：
- PNG (.png) - 推荐，支持透明度
- JPEG (.jpg, .jpeg)
- BMP (.bmp)

## 文件命名

建议使用描述性名称，例如：
- `login_button.png`
- `game_icon.png`
- `enemy_health_bar.png`

## 最佳实践

1. **裁剪精确**：模板图像应该只包含需要识别的元素，不要包含太多周围内容
2. **清晰度**：使用高清晰度的图像以提高识别准确率
3. **多样性**：为同一元素的不同状态创建多个模板（如按钮的正常、悬停、按下状态）
4. **命名规范**：使用一致的命名规范，便于管理和使用

## 使用方法

在GUI中，您可以通过"添加模板"功能添加新的模板图像。

在代码中，您可以使用`ImageRecognition`类的方法来使用这些模板：

```python
from src.image_recognition import ImageRecognition
from src.screen_capture import ScreenCapture

# 初始化
ir = ImageRecognition()
sc = ScreenCapture()

# 捕获屏幕
screen = sc.capture_screen()

# 查找模板
locations = ir.find_template(screen, "login_button")
if locations:
    x, y, w, h, confidence = locations[0]
    print(f"找到按钮，位置: ({x}, {y}), 置信度: {confidence}")
```
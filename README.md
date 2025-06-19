# 游戏自动化脚本工具

这是一个功能强大的游戏自动化工具，支持录制和回放鼠标键盘操作、图像识别、OCR文字识别等功能。

## 主要功能

- **录制和回放**
  - 录制鼠标移动、点击和键盘操作
  - 支持回放速度调节
  - 管理和组织录制文件

- **图像识别**
  - 模板匹配
  - OCR文字识别
  - 图像相似度比较
  - 特征点检测
  - 边缘和轮廓检测

- **屏幕捕获**
  - 全屏或区域截图
  - 实时屏幕预览
  - FPS监控
  - 像素颜色检测

- **图形界面**
  - 直观的操作界面
  - 实时预览
  - 参数配置
  - 文件管理

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/game_automation_script.git
cd game_automation_script
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装Tesseract-OCR（用于文字识别）：
- Windows: 下载并安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

## 使用方法

### 图形界面

运行主程序：
```bash
python src/main.py
```

### 命令行

运行示例脚本：
```bash
python examples/basic_automation.py
```

### 基本用法

1. **录制操作**
   - 打开程序，切换到"录制"标签页
   - 点击"开始录制"按钮
   - 执行要录制的操作
   - 点击"停止录制"按钮
   - 输入名称保存录制

2. **回放操作**
   - 切换到"回放"标签页
   - 从列表中选择录制文件
   - 调整回放速度（可选）
   - 点击"开始回放"按钮

3. **图像识别**
   - 切换到"识别"标签页
   - 添加模板图像
   - 设置匹配参数
   - 点击"开始识别"按钮

## 示例代码

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
from src.event_player import EventPlayer

# 初始化组件
screen_capture = ScreenCapture()
image_recognition = ImageRecognition()
event_player = EventPlayer()

# 捕获屏幕
screen = screen_capture.capture_screen()

# 查找模板
locations = image_recognition.find_template(screen, "template_name")

# 回放录制
event_player.load_recording("recording_name")
event_player.start_playback()
```

## 配置

- 录制文件保存在 `recordings` 目录
- 模板图像保存在 `templates` 目录
- 日志文件保存在 `logs` 目录

## 注意事项

1. 使用管理员权限运行可以避免某些权限问题
2. 部分游戏可能限制外部程序的操作
3. 建议在测试环境中先进行验证
4. 使用前请备份重要数据

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交问题和改进建议！

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request
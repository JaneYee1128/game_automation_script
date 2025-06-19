# 日志文件目录

此目录用于存储游戏自动化脚本工具生成的日志文件。

日志文件记录了工具运行过程中的各种事件、错误和调试信息，对于排查问题和了解工具运行状态非常有用。

## 文件命名

日志文件通常以以下格式命名：
```
game_automation_YYYY-MM-DD.log
```

例如：`game_automation_2024-06-18.log`

## 日志级别

日志记录使用以下级别：
- **DEBUG**：详细的调试信息
- **INFO**：一般信息性消息
- **WARNING**：警告信息，表示可能的问题
- **ERROR**：错误信息，表示发生了错误但程序仍在运行
- **CRITICAL**：严重错误，可能导致程序终止

## 日志格式

日志条目的基本格式如下：
```
2024-06-18 15:30:45,123 - ScreenCapture - INFO - 成功捕获屏幕，分辨率：1920x1080
2024-06-18 15:30:46,456 - EventPlayer - WARNING - 无法加载录制文件：file_not_found.json
2024-06-18 15:30:47,789 - ImageRecognition - ERROR - 模板匹配失败：找不到模板文件 'missing_template.png'
```

## 配置日志

您可以通过修改`main.py`或其他模块中的日志配置来调整日志级别和格式：

```python
import logging

# 基本配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/game_automation_2024-06-18.log',
    filemode='a'
)

# 获取特定模块的日志记录器
logger = logging.getLogger('ScreenCapture')
logger.setLevel(logging.DEBUG)  # 为此模块设置更详细的日志级别
```

## 日志文件管理

日志文件可能会随着时间增长。建议定期归档或删除旧的日志文件，以避免占用过多磁盘空间。
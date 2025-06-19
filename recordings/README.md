# 录制文件目录

此目录用于存储通过游戏自动化脚本工具录制的事件序列文件。

录制文件格式为JSON，包含时间戳和事件类型等信息。

## 文件命名

录制文件通常以以下格式命名：
```
recording_YYYY-MM-DD_HH-MM-SS.json
```

例如：`recording_2024-06-18_15-30-45.json`

## 文件结构

录制文件的基本结构如下：
```json
{
  "name": "示例录制",
  "created_at": "2024-06-18 15:30:45",
  "duration": 10.5,
  "events": [
    {
      "type": "MOUSE_MOVE",
      "x": 100,
      "y": 200,
      "time": 0.0
    },
    {
      "type": "MOUSE_CLICK",
      "button": "left",
      "x": 100,
      "y": 200,
      "time": 1.5
    }
    // 更多事件...
  ]
}
```
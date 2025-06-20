# 更新日志

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2024-01-20

### 新增
- 基础功能实现
  - 屏幕捕获模块
  - 事件录制模块
  - 事件回放模块
  - 图像识别模块
- 图形用户界面
  - 录制和回放控制
  - 实时屏幕预览
  - 参数配置界面
- 基本示例脚本
- 完整的文档
  - 用户指南
  - API参考
  - 使用示例
  - 贡献指南

### 依赖
- opencv-python >= 4.5.0
- numpy >= 1.19.0
- Pillow >= 8.0.0
- pyautogui >= 0.9.50
- pynput >= 1.7.0
- pytesseract >= 0.3.0
- scikit-image >= 0.18.0
- scikit-learn >= 0.24.0

### 已知问题
- 在某些游戏中可能无法正常捕获屏幕
- OCR文字识别准确率需要提升
- 高DPI屏幕下可能存在坐标偏移

## [0.0.1] - 2024-01-10

### 新增
- 项目初始化
- 基本项目结构搭建
- 核心模块框架
- 基础依赖配置
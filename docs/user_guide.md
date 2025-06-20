# 游戏自动化脚本工具 - 用户指南

本指南将帮助您了解如何使用游戏自动化脚本工具的各项功能。

## 目录

1. [安装与设置](#安装与设置)
2. [图形界面概述](#图形界面概述)
3. [录制功能](#录制功能)
4. [回放功能](#回放功能)
5. [图像识别功能](#图像识别功能)
6. [屏幕捕获功能](#屏幕捕获功能)
7. [高级设置](#高级设置)
8. [常见问题解答](#常见问题解答)

## 安装与设置

### 系统要求

- 操作系统：Windows 7/8/10/11, macOS 10.14+, Linux
- Python 版本：3.7 - 3.10
- 内存：至少 4GB RAM
- 硬盘空间：至少 500MB 可用空间

### 安装步骤

1. **安装 Python**
   - 从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python
   - 确保在安装时勾选"Add Python to PATH"选项

2. **安装 Tesseract-OCR**（用于文字识别功能）
   - Windows: 从 [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装
   - Linux: 执行 `sudo apt-get install tesseract-ocr`
   - macOS: 执行 `brew install tesseract`

3. **安装游戏自动化脚本工具**
   ```bash
   # 克隆仓库
   git clone https://github.com/yourusername/game_automation_script.git
   cd game_automation_script
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 安装工具
   pip install -e .
   ```

4. **验证安装**
   ```bash
   # 运行主程序
   python src/main.py
   ```

## 图形界面概述

启动程序后，您将看到分为左右两部分的界面：

### 左侧控制面板

包含四个标签页：

1. **录制**：用于录制鼠标和键盘操作
   - 开始/停止录制按钮
   - 录制文件列表
   - 保存/加载录制选项

2. **回放**：用于回放已录制的操作
   - 开始/停止/暂停回放按钮
   - 回放速度调节滑块
   - 录制文件选择下拉框

3. **识别**：用于图像识别和模板匹配
   - 模板管理（添加/删除/预览）
   - 识别参数设置
   - 识别结果显示

4. **设置**：用于配置工具参数
   - 屏幕捕获区域设置
   - 捕获间隔设置
   - 日志级别设置
   - 其他全局设置

### 右侧预览面板

- 显示实时屏幕预览
- 显示识别结果（如匹配区域高亮）
- 显示捕获区域边界
- 显示FPS和状态信息

## 录制功能

录制功能允许您捕获鼠标和键盘操作，以便后续回放。

### 开始录制

1. 切换到"录制"标签页
2. 点击"开始录制"按钮
3. 执行您想要录制的操作
4. 点击"停止录制"按钮
5. 在弹出的对话框中输入录制名称
6. 点击"保存"按钮

### 录制设置

- **录制区域**：可以选择全屏录制或指定区域录制
- **事件过滤**：可以选择只录制鼠标事件、只录制键盘事件或两者都录制
- **鼠标移动节流**：控制鼠标移动事件的记录频率，避免生成过大的录制文件

### 管理录制文件

- **查看录制列表**：在录制标签页可以看到所有保存的录制文件
- **加载录制**：双击列表中的录制文件或选择后点击"加载"按钮
- **删除录制**：选择录制文件后点击"删除"按钮
- **重命名录制**：选择录制文件后点击"重命名"按钮

## 回放功能

回放功能允许您重现之前录制的操作序列。

### 开始回放

1. 切换到"回放"标签页
2. 从下拉列表中选择要回放的录制文件
3. 调整回放速度（可选）
4. 点击"开始回放"按钮

### 回放控制

- **暂停/恢复**：点击"暂停"按钮暂停回放，再次点击恢复回放
- **停止**：点击"停止"按钮终止回放
- **速度调节**：使用滑块调整回放速度（0.5x - 2.0x）
- **循环回放**：勾选"循环"复选框可以重复回放

### 回放设置

- **相对坐标**：启用后，回放时会相对于当前捕获区域的左上角进行坐标转换
- **错误处理**：设置回放遇到错误时的行为（继续、暂停或停止）
- **超时设置**：设置回放操作的最大等待时间

## 图像识别功能

图像识别功能允许您在屏幕上查找特定图像或文字。

### 模板匹配

1. 切换到"识别"标签页
2. 点击"添加模板"按钮
3. 选择模板图像文件
4. 设置匹配阈值（0.0-1.0，值越高要求越精确）
5. 点击"开始识别"按钮

### OCR文字识别

1. 切换到"识别"标签页
2. 选择"OCR"选项卡
3. 输入要查找的文字
4. 设置语言和其他OCR参数
5. 点击"开始识别"按钮

### 高级识别功能

- **颜色检测**：查找屏幕上特定颜色的区域
- **边缘检测**：识别屏幕上的边缘和轮廓
- **特征点匹配**：使用SIFT/SURF等算法进行特征点匹配
- **图像比较**：比较两个图像的相似度

## 屏幕捕获功能

屏幕捕获功能是其他功能的基础，提供实时屏幕内容。

### 捕获设置

1. 切换到"设置"标签页
2. 在"捕获设置"部分：
   - 设置捕获区域（全屏或自定义区域）
   - 设置捕获间隔（毫秒）
   - 设置捕获质量（影响性能）

### 捕获区域选择

1. 点击"选择区域"按钮
2. 在弹出的全屏窗口中拖动鼠标选择区域
3. 点击"确认"按钮保存选择

### 捕获预览

- 右侧预览面板实时显示捕获内容
- 显示FPS（每秒帧数）信息
- 可以暂停/恢复预览

## 高级设置

### 全局设置

- **语言设置**：选择界面语言
- **主题设置**：选择明亮或暗黑主题
- **日志级别**：设置日志详细程度（调试、信息、警告、错误）

### 性能设置

- **线程数**：设置图像处理使用的线程数
- **缓存大小**：设置图像缓存大小
- **优化选项**：根据系统配置自动优化性能

### 热键设置

- 设置开始/停止录制的热键
- 设置开始/停止回放的热键
- 设置紧急停止的热键

## 常见问题解答

### 录制问题

**Q: 为什么我的录制没有捕获某些按键？**  
A: 某些系统级热键或被游戏拦截的按键可能无法被捕获。尝试使用管理员权限运行程序。

**Q: 录制文件可以编辑吗？**  
A: 目前不支持直接编辑录制文件，但您可以使用文本编辑器打开JSON格式的录制文件进行手动编辑。

### 回放问题

**Q: 回放时鼠标位置不准确怎么办？**  
A: 确保回放时的屏幕分辨率和录制时相同，或启用"相对坐标"选项。

**Q: 如何在特定条件下停止回放？**  
A: 可以使用图像识别功能配合条件触发器来控制回放流程。

### 图像识别问题

**Q: 为什么模板匹配找不到明显存在的图像？**  
A: 尝试降低匹配阈值，或确保模板图像与实际屏幕上的图像完全一致（包括大小和颜色）。

**Q: OCR识别准确率低怎么办？**  
A: 尝试调整OCR参数，如语言设置、预处理选项，或使用更清晰的屏幕区域。

### 系统问题

**Q: 程序占用CPU过高怎么办？**  
A: 尝试降低捕获帧率，减小捕获区域，或调整性能设置。

**Q: 在某些游戏中无法正常工作？**  
A: 某些游戏使用反作弊系统可能会限制外部程序的操作。尝试以兼容模式运行游戏或使用管理员权限运行本工具。
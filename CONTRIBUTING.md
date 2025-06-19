# 贡献指南

感谢您对游戏自动化脚本工具的关注！我们欢迎各种形式的贡献，包括但不限于：

- 代码贡献
- 文档改进
- Bug报告
- 功能建议
- 使用示例

## 目录

1. [开发环境设置](#开发环境设置)
2. [代码风格](#代码风格)
3. [提交Pull Request](#提交pull-request)
4. [报告Bug](#报告bug)
5. [提出建议](#提出建议)

## 开发环境设置

1. Fork本仓库并克隆到本地：
```bash
git clone https://github.com/yourusername/game_automation_script.git
cd game_automation_script
```

2. 创建并激活虚拟环境：
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. 安装开发依赖：
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发专用依赖
```

4. 安装pre-commit钩子：
```bash
pre-commit install
```

## 代码风格

我们使用以下工具来保持代码质量：

- black：代码格式化
- flake8：代码风格检查
- mypy：类型检查
- isort：导入语句排序

请确保您的代码符合以下标准：

1. 使用类型注解：
```python
def add_numbers(a: int, b: int) -> int:
    return a + b
```

2. 编写文档字符串：
```python
def find_template(
    image: np.ndarray,
    template_name: str,
    threshold: float = 0.8
) -> List[Tuple[int, int, int, int, float]]:
    """
    在图像中查找模板。

    Args:
        image: 要搜索的图像
        template_name: 模板名称
        threshold: 匹配阈值，默认为0.8

    Returns:
        匹配结果列表，每个元素为(x, y, w, h, confidence)
    
    Raises:
        ImageRecognitionError: 当模板文件不存在或无法读取时
    """
```

3. 遵循PEP 8命名约定：
- 类名使用CamelCase
- 函数和变量名使用snake_case
- 常量使用UPPER_CASE

4. 保持函数简短且职责单一

5. 编写单元测试：
```python
def test_find_template():
    recognition = ImageRecognition()
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    template = np.ones((20, 20, 3), dtype=np.uint8)
    
    # 保存测试模板
    cv2.imwrite("test_template.png", template)
    
    # 测试查找模板
    results = recognition.find_template(image, "test_template")
    assert len(results) == 0  # 应该找不到匹配
    
    # 清理测试文件
    os.remove("test_template.png")
```

## 提交Pull Request

1. 创建新分支：
```bash
git checkout -b feature/your-feature-name
```

2. 进行更改并提交：
```bash
git add .
git commit -m "feat: add new feature"
```

3. 推送到您的Fork：
```bash
git push origin feature/your-feature-name
```

4. 在GitHub上创建Pull Request

提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- feat：新功能
- fix：修复bug
- docs：文档更改
- style：不影响代码含义的更改（空格、格式化等）
- refactor：既不修复bug也不添加功能的代码更改
- perf：改进性能的代码更改
- test：添加或修正测试
- chore：对构建过程或辅助工具的更改

示例：
```
feat(image-recognition): add circle detection

Add Hough Circle Transform algorithm to detect circles in images.
The new feature supports:
- Circle detection with configurable parameters
- Multiple circles detection in single image
- Circle radius filtering

Closes #123
```

## 报告Bug

创建Issue时，请包含：

1. 问题描述
2. 复现步骤
3. 期望行为
4. 实际行为
5. 环境信息：
   - 操作系统
   - Python版本
   - 依赖包版本
   - 错误日志

## 提出建议

创建Issue时，请包含：

1. 功能描述
2. 使用场景
3. 预期效果
4. 可能的实现方式
5. 相关参考资料

## 开发流程

1. 选择要处理的Issue
2. 在Issue上发表评论，表明您要处理它
3. Fork仓库并克隆到本地
4. 创建新分支
5. 进行开发
6. 编写测试
7. 运行测试并确保通过
8. 提交代码
9. 创建Pull Request

## 发布流程

1. 更新版本号（遵循语义化版本）
2. 更新CHANGELOG.md
3. 创建发布标签
4. 构建分发包
5. 上传到PyPI

## 项目结构

```
game_automation_script/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── event_recorder.py   # 事件录制
│   ├── event_player.py     # 事件回放
│   ├── image_recognition.py # 图像识别
│   ├── screen_capture.py   # 屏幕捕获
│   └── gui.py             # 图形界面
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_event_recorder.py
│   ├── test_event_player.py
│   ├── test_image_recognition.py
│   └── test_screen_capture.py
├── docs/                   # 文档
│   ├── user_guide.md
│   ├── api_reference.md
│   └── examples.md
├── examples/               # 示例
│   ├── __init__.py
│   └── basic_automation.py
├── scripts/               # 工具脚本
│   ├── build.py
│   └── release.py
├── .github/               # GitHub配置
│   └── workflows/         # GitHub Actions
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── setup.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── tox.ini
```

## 许可证

通过提交代码，您同意您的贡献将在MIT许可证下发布。
"""
核心功能模块
提供游戏自动化脚本系统的核心功能，包括截图、录制、回放和脚本执行等
"""

from .capture import ScreenCapture
from .recorder import InputRecorder
from .player import InputPlayer
from .script import ScriptExecutor

__all__ = ['ScreenCapture', 'InputRecorder', 'InputPlayer', 'ScriptExecutor']
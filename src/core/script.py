"""
脚本执行引擎模块
提供脚本的解析、执行和管理功能
"""

import os
import time
import json
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from enum import Enum
from datetime import datetime

# 导入项目模块
from logger import get_logger
from config import config
from core.capture import ScreenCapture
from core.recorder import InputEvent, MouseEvent, KeyboardEvent, WaitEvent
from core.player import InputPlayer

# 获取日志记录器
logger = get_logger(__name__)


class ScriptStepType(Enum):
    """脚本步骤类型"""
    CLICK = "click"                # 点击
    RIGHT_CLICK = "right_click"    # 右键点击
    DOUBLE_CLICK = "double_click"  # 双击
    MOVE = "move"                  # 移动鼠标
    TYPE = "type"                  # 输入文本
    KEY = "key"                    # 按键
    WAIT = "wait"                  # 等待
    FIND_IMAGE = "find_image"      # 查找图像
    FIND_TEXT = "find_text"        # 查找文本
    EXECUTE = "execute"            # 执行录制
    CONDITION = "condition"        # 条件判断
    LOOP = "loop"                  # 循环
    COMMENT = "comment"            # 注释


class ScriptStep:
    """脚本步骤"""
    
    def __init__(
        self,
        step_id: str,
        step_type: ScriptStepType,
        params: Dict[str, Any],
        description: str = ""
    ):
        """
        初始化脚本步骤
        
        参数:
            step_id: 步骤ID
            step_type: 步骤类型
            params: 步骤参数
            description: 步骤描述
        """
        self.step_id = step_id
        self.step_type = step_type
        self.params = params
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 步骤字典
        """
        return {
            "id": self.step_id,
            "type": self.step_type.value,
            "params": self.params,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScriptStep':
        """
        从字典创建步骤
        
        参数:
            data: 步骤字典
        
        返回:
            ScriptStep: 脚本步骤对象
        """
        return cls(
            data["id"],
            ScriptStepType(data["type"]),
            data["params"],
            data.get("description", "")
        )


class Script:
    """脚本类"""
    
    def __init__(
        self,
        script_id: str,
        name: str,
        description: str = "",
        author: str = "",
        version: str = "1.0",
        steps: Optional[List[ScriptStep]] = None
    ):
        """
        初始化脚本
        
        参数:
            script_id: 脚本ID
            name: 脚本名称
            description: 脚本描述
            author: 作者
            version: 版本
            steps: 步骤列表
        """
        self.script_id = script_id
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.steps = steps or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def add_step(self, step: ScriptStep) -> None:
        """
        添加步骤
        
        参数:
            step: 脚本步骤
        """
        self.steps.append(step)
        self.updated_at = datetime.now().isoformat()
    
    def remove_step(self, step_id: str) -> bool:
        """
        移除步骤
        
        参数:
            step_id: 步骤ID
        
        返回:
            bool: 是否成功移除
        """
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                self.steps.pop(i)
                self.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def update_step(self, step_id: str, new_step: ScriptStep) -> bool:
        """
        更新步骤
        
        参数:
            step_id: 步骤ID
            new_step: 新步骤
        
        返回:
            bool: 是否成功更新
        """
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                self.steps[i] = new_step
                self.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def move_step(self, step_id: str, new_index: int) -> bool:
        """
        移动步骤
        
        参数:
            step_id: 步骤ID
            new_index: 新索引
        
        返回:
            bool: 是否成功移动
        """
        # 查找步骤
        step_index = -1
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                step_index = i
                break
        
        if step_index == -1:
            return False
        
        # 限制索引范围
        new_index = max(0, min(new_index, len(self.steps) - 1))
        
        # 移动步骤
        if step_index != new_index:
            step = self.steps.pop(step_index)
            self.steps.insert(new_index, step)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 脚本字典
        """
        return {
            "id": self.script_id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "steps": [step.to_dict() for step in self.steps]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Script':
        """
        从字典创建脚本
        
        参数:
            data: 脚本字典
        
        返回:
            Script: 脚本对象
        """
        script = cls(
            data["id"],
            data["name"],
            data.get("description", ""),
            data.get("author", ""),
            data.get("version", "1.0")
        )
        
        script.created_at = data.get("created_at", script.created_at)
        script.updated_at = data.get("updated_at", script.updated_at)
        
        # 添加步骤
        for step_data in data.get("steps", []):
            script.steps.append(ScriptStep.from_dict(step_data))
        
        return script
    
    def save(self, file_path: str) -> bool:
        """
        保存脚本
        
        参数:
            file_path: 文件路径
        
        返回:
            bool: 是否成功保存
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 保存为JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"已保存脚本: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"保存脚本失败: {str(e)}")
            return False
    
    @classmethod
    def load(cls, file_path: str) -> Optional['Script']:
        """
        加载脚本
        
        参数:
            file_path: 文件路径
        
        返回:
            Optional[Script]: 脚本对象，如果加载失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"脚本文件不存在: {file_path}")
                return None
            
            # 加载JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建脚本对象
            script = cls.from_dict(data)
            
            logger.info(f"已加载脚本: {file_path}")
            return script
        
        except Exception as e:
            logger.error(f"加载脚本失败: {str(e)}")
            return None


class ScriptExecutionResult:
    """脚本执行结果"""
    
    def __init__(
        self,
        success: bool,
        message: str = "",
        step_id: Optional[str] = None,
        step_index: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        初始化执行结果
        
        参数:
            success: 是否成功
            message: 结果消息
            step_id: 步骤ID
            step_index: 步骤索引
            data: 结果数据
        """
        self.success = success
        self.message = message
        self.step_id = step_id
        self.step_index = step_index
        self.data = data or {}


class ScriptExecutor:
    """脚本执行器"""
    
    def __init__(self):
        """初始化执行器"""
        self.script: Optional[Script] = None
        self.executing = False
        self.paused = False
        self.current_step_index = 0
        
        # 线程
        self.execute_thread = None
        
        # 回调函数
        self.on_step_start = None
        self.on_step_complete = None
        self.on_script_complete = None
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 工具
        self.screen_capture = ScreenCapture()
        self.input_player = InputPlayer()
        
        # 变量存储
        self.variables = {}
        
        logger.debug("脚本执行器已初始化")
    
    def load_script(self, script: Script) -> None:
        """
        加载脚本
        
        参数:
            script: 脚本对象
        """
        with self.lock:
            self.script = script
            self.current_step_index = 0
        
        logger.debug(f"已加载脚本: {script.name}")
    
    def execute(
        self,
        on_step_start: Optional[Callable[[ScriptStep, int], None]] = None,
        on_step_complete: Optional[Callable[[ScriptStep, int, ScriptExecutionResult], None]] = None,
        on_script_complete: Optional[Callable[[bool, str], None]] = None
    ) -> bool:
        """
        执行脚本
        
        参数:
            on_step_start: 步骤开始回调
            on_step_complete: 步骤完成回调
            on_script_complete: 脚本完成回调
        
        返回:
            bool: 是否成功开始执行
        """
        if self.executing:
            logger.warning("脚本已经在执行中")
            return False
        
        if not self.script:
            logger.warning("没有加载脚本")
            return False
        
        if not self.script.steps:
            logger.warning("脚本没有步骤")
            return False
        
        try:
            with self.lock:
                self.executing = True
                self.paused = False
                self.current_step_index = 0
                self.on_step_start = on_step_start
                self.on_step_complete = on_step_complete
                self.on_script_complete = on_script_complete
                self.variables = {}
            
            # 创建执行线程
            self.execute_thread = threading.Thread(target=self._execute_thread)
            self.execute_thread.daemon = True
            self.execute_thread.start()
            
            logger.info(f"开始执行脚本: {self.script.name}")
            return True
        
        except Exception as e:
            logger.error(f"开始执行脚本失败: {str(e)}")
            self.executing = False
            return False
    
    def stop(self) -> None:
        """停止执行"""
        if not self.executing:
            return
        
        with self.lock:
            self.executing = False
            self.paused = False
        
        logger.info("停止执行脚本")
    
    def pause(self) -> None:
        """暂停执行"""
        if not self.executing or self.paused:
            return
        
        with self.lock:
            self.paused = True
        
        logger.info("暂停执行脚本")
    
    def resume(self) -> None:
        """恢复执行"""
        if not self.executing or not self.paused:
            return
        
        with self.lock:
            self.paused = False
        
        logger.info("恢复执行脚本")
    
    def _execute_thread(self) -> None:
        """执行线程"""
        success = True
        message = "执行完成"
        
        try:
            while self.executing and self.current_step_index < len(self.script.steps):
                # 检查是否暂停
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # 获取当前步骤
                with self.lock:
                    if self.current_step_index >= len(self.script.steps):
                        break
                    
                    step = self.script.steps[self.current_step_index]
                    step_index = self.current_step_index
                
                # 调用步骤开始回调
                if self.on_step_start:
                    self.on_step_start(step, step_index)
                
                # 执行步骤
                result = self._execute_step(step, step_index)
                
                # 调用步骤完成回调
                if self.on_step_complete:
                    self.on_step_complete(step, step_index, result)
                
                # 检查步骤执行结果
                if not result.success:
                    success = False
                    message = f"步骤 {step_index + 1} 执行失败: {result.message}"
                    break
                
                # 更新步骤索引
                with self.lock:
                    self.current_step_index += 1
            
            # 执行完成
            with self.lock:
                self.executing = False
                self.paused = False
            
            # 调用脚本完成回调
            if self.on_script_complete:
                self.on_script_complete(success, message)
            
            logger.info(f"脚本执行完成: {message}")
        
        except Exception as e:
            logger.error(f"脚本执行线程异常: {str(e)}")
            
            with self.lock:
                self.executing = False
                self.paused = False
            
            # 调用脚本完成回调
            if self.on_script_complete:
                self.on_script_complete(False, f"执行异常: {str(e)}")
    
    def _execute_step(self, step: ScriptStep, step_index: int) -> ScriptExecutionResult:
        """
        执行单个步骤
        
        参数:
            step: 脚本步骤
            step_index: 步骤索引
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            logger.debug(f"执行步骤 {step_index + 1}: {step.step_type.value}")
            
            # 根据步骤类型执行
            if step.step_type == ScriptStepType.CLICK:
                return self._execute_click(step)
            elif step.step_type == ScriptStepType.RIGHT_CLICK:
                return self._execute_right_click(step)
            elif step.step_type == ScriptStepType.DOUBLE_CLICK:
                return self._execute_double_click(step)
            elif step.step_type == ScriptStepType.MOVE:
                return self._execute_move(step)
            elif step.step_type == ScriptStepType.TYPE:
                return self._execute_type(step)
            elif step.step_type == ScriptStepType.KEY:
                return self._execute_key(step)
            elif step.step_type == ScriptStepType.WAIT:
                return self._execute_wait(step)
            elif step.step_type == ScriptStepType.FIND_IMAGE:
                return self._execute_find_image(step)
            elif step.step_type == ScriptStepType.FIND_TEXT:
                return self._execute_find_text(step)
            elif step.step_type == ScriptStepType.EXECUTE:
                return self._execute_recording(step)
            elif step.step_type == ScriptStepType.CONDITION:
                return self._execute_condition(step)
            elif step.step_type == ScriptStepType.LOOP:
                return self._execute_loop(step)
            elif step.step_type == ScriptStepType.COMMENT:
                return ScriptExecutionResult(True, "注释步骤", step.step_id, step_index)
            else:
                return ScriptExecutionResult(False, f"未知步骤类型: {step.step_type.value}", step.step_id, step_index)
        
        except Exception as e:
            logger.error(f"执行步骤失败: {str(e)}")
            return ScriptExecutionResult(False, f"执行异常: {str(e)}", step.step_id, step_index)
    
    def _execute_click(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行点击步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            x = step.params.get("x", 0)
            y = step.params.get("y", 0)
            
            # 执行点击
            import pyautogui
            pyautogui.click(x, y)
            
            return ScriptExecutionResult(True, f"点击位置 ({x}, {y})", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"点击失败: {str(e)}", step.step_id)
    
    def _execute_right_click(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行右键点击步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            x = step.params.get("x", 0)
            y = step.params.get("y", 0)
            
            # 执行右键点击
            import pyautogui
            pyautogui.rightClick(x, y)
            
            return ScriptExecutionResult(True, f"右键点击位置 ({x}, {y})", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"右键点击失败: {str(e)}", step.step_id)
    
    def _execute_double_click(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行双击步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            x = step.params.get("x", 0)
            y = step.params.get("y", 0)
            
            # 执行双击
            import pyautogui
            pyautogui.doubleClick(x, y)
            
            return ScriptExecutionResult(True, f"双击位置 ({x}, {y})", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"双击失败: {str(e)}", step.step_id)
    
    def _execute_move(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行移动鼠标步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            x = step.params.get("x", 0)
            y = step.params.get("y", 0)
            
            # 执行移动
            import pyautogui
            pyautogui.moveTo(x, y)
            
            return ScriptExecutionResult(True, f"移动鼠标到位置 ({x}, {y})", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"移动鼠标失败: {str(e)}", step.step_id)
    
    def _execute_type(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行输入文本步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            text = step.params.get("text", "")
            interval = step.params.get("interval", 0.0)
            
            # 执行输入
            import pyautogui
            pyautogui.write(text, interval=interval)
            
            return ScriptExecutionResult(True, f"输入文本: {text}", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"输入文本失败: {str(e)}", step.step_id)
    
    def _execute_key(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行按键步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            key = step.params.get("key", "")
            
            # 执行按键
            import pyautogui
            pyautogui.press(key)
            
            return ScriptExecutionResult(True, f"按键: {key}", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"按键失败: {str(e)}", step.step_id)
    
    def _execute_wait(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行等待步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            seconds = step.params.get("seconds", 1.0)
            
            # 执行等待
            time.sleep(seconds)
            
            return ScriptExecutionResult(True, f"等待 {seconds} 秒", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"等待失败: {str(e)}", step.step_id)
    
    def _execute_find_image(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行查找图像步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            image_path = step.params.get("image_path", "")
            threshold = step.params.get("threshold", 0.8)
            max_wait = step.params.get("max_wait", 0.0)
            region = step.params.get("region")
            click = step.params.get("click", False)
            
            # 检查图像路径
            if not image_path or not os.path.exists(image_path):
                return ScriptExecutionResult(False, f"图像文件不存在: {image_path}", step.step_id)
            
            # 查找图像
            result = self.screen_capture.find_image(
                image_path,
                threshold=threshold,
                region=region,
                max_wait=max_wait
            )
            
            if not result:
                return ScriptExecutionResult(False, f"未找到图像: {image_path}", step.step_id)
            
            # 如果需要点击
            if click:
                left, top, right, bottom = result
                x = (left + right) // 2
                y = (top + bottom) // 2
                
                import pyautogui
                pyautogui.click(x, y)
            
            return ScriptExecutionResult(
                True,
                f"找到图像: {image_path}，位置: {result}",
                step.step_id,
                data={"region": result}
            )
        
        except Exception as e:
            return ScriptExecutionResult(False, f"查找图像失败: {str(e)}", step.step_id)
    
    def _execute_find_text(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行查找文本步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            text = step.params.get("text", "")
            lang = step.params.get("lang", "eng")
            max_wait = step.params.get("max_wait", 0.0)
            region = step.params.get("region")
            click = step.params.get("click", False)
            
            # 检查文本
            if not text:
                return ScriptExecutionResult(False, "未指定要查找的文本", step.step_id)
            
            # 查找文本
            result = self.screen_capture.find_text(
                text,
                lang=lang,
                region=region,
                max_wait=max_wait
            )
            
            if not result:
                return ScriptExecutionResult(False, f"未找到文本: {text}", step.step_id)
            
            # 如果需要点击
            if click:
                left, top, right, bottom = result
                x = (left + right) // 2
                y = (top + bottom) // 2
                
                import pyautogui
                pyautogui.click(x, y)
            
            return ScriptExecutionResult(
                True,
                f"找到文本: {text}，位置: {result}",
                step.step_id,
                data={"region": result}
            )
        
        except Exception as e:
            return ScriptExecutionResult(False, f"查找文本失败: {str(e)}", step.step_id)
    
    def _execute_recording(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行录制步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            recording_path = step.params.get("recording_path", "")
            speed = step.params.get("speed", 1.0)
            
            # 检查录制文件
            if not recording_path or not os.path.exists(recording_path):
                return ScriptExecutionResult(False, f"录制文件不存在: {recording_path}", step.step_id)
            
            # 加载录制文件
            if not self.input_player.load_recording(recording_path):
                return ScriptExecutionResult(False, f"加载录制文件失败: {recording_path}", step.step_id)
            
            # 回放录制
            completed = threading.Event()
            
            def on_complete():
                completed.set()
            
            self.input_player.start_playback(on_complete=on_complete, speed=speed)
            
            # 等待回放完成
            completed.wait()
            
            return ScriptExecutionResult(True, f"执行录制: {recording_path}", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"执行录制失败: {str(e)}", step.step_id)
    
    def _execute_condition(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行条件判断步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            condition_type = step.params.get("condition_type", "")
            condition_params = step.params.get("condition_params", {})
            true_step = step.params.get("true_step")
            false_step = step.params.get("false_step")
            
            # 执行条件判断
            condition_result = False
            
            if condition_type == "image_exists":
                # 检查图像是否存在
                image_path = condition_params.get("image_path", "")
                threshold = condition_params.get("threshold", 0.8)
                region = condition_params.get("region")
                
                if image_path and os.path.exists(image_path):
                    result = self.screen_capture.find_image(
                        image_path,
                        threshold=threshold,
                        region=region
                    )
                    condition_result = bool(result)
            
            elif condition_type == "text_exists":
                # 检查文本是否存在
                text = condition_params.get("text", "")
                lang = condition_params.get("lang", "eng")
                region = condition_params.get("region")
                
                if text:
                    result = self.screen_capture.find_text(
                        text,
                        lang=lang,
                        region=region
                    )
                    condition_result = bool(result)
            
            elif condition_type == "variable_equals":
                # 检查变量是否等于指定值
                variable_name = condition_params.get("variable_name", "")
                value = condition_params.get("value")
                
                if variable_name in self.variables:
                    condition_result = self.variables[variable_name] == value
            
            # 根据条件结果执行相应步骤
            if condition_result:
                if true_step:
                    true_step_obj = ScriptStep.from_dict(true_step)
                    return self._execute_step(true_step_obj, -1)
                return ScriptExecutionResult(True, "条件为真，无操作", step.step_id)
            else:
                if false_step:
                    false_step_obj = ScriptStep.from_dict(false_step)
                    return self._execute_step(false_step_obj, -1)
                return ScriptExecutionResult(True, "条件为假，无操作", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"条件判断失败: {str(e)}", step.step_id)
    
    def _execute_loop(self, step: ScriptStep) -> ScriptExecutionResult:
        """
        执行循环步骤
        
        参数:
            step: 脚本步骤
        
        返回:
            ScriptExecutionResult: 执行结果
        """
        try:
            # 获取参数
            loop_type = step.params.get("loop_type", "")
            loop_params = step.params.get("loop_params", {})
            loop_step = step.params.get("loop_step")
            
            # 检查循环步骤
            if not loop_step:
                return ScriptExecutionResult(False, "未指定循环步骤", step.step_id)
            
            loop_step_obj = ScriptStep.from_dict(loop_step)
            
            # 执行循环
            if loop_type == "count":
                # 计数循环
                count = loop_params.get("count", 1)
                
                for i in range(count):
                    # 检查是否停止执行
                    if not self.executing or self.paused:
                        break
                    
                    # 执行循环步骤
                    result = self._execute_step(loop_step_obj, -1)
                    
                    # 检查步骤执行结果
                    if not result.success:
                        return ScriptExecutionResult(
                            False,
                            f"循环第 {i + 1} 次执行失败: {result.message}",
                            step.step_id
                        )
                
                return ScriptExecutionResult(True, f"完成 {count} 次循环", step.step_id)
            
            elif loop_type == "until_image":
                # 直到图像出现/消失循环
                image_path = loop_params.get("image_path", "")
                threshold = loop_params.get("threshold", 0.8)
                region = loop_params.get("region")
                until_found = loop_params.get("until_found", True)
                max_iterations = loop_params.get("max_iterations", 10)
                
                # 检查图像路径
                if not image_path or not os.path.exists(image_path):
                    return ScriptExecutionResult(False, f"图像文件不存在: {image_path}", step.step_id)
                
                for i in range(max_iterations):
                    # 检查是否停止执行
                    if not self.executing or self.paused:
                        break
                    
                    # 执行循环步骤
                    result = self._execute_step(loop_step_obj, -1)
                    
                    # 检查步骤执行结果
                    if not result.success:
                        return ScriptExecutionResult(
                            False,
                            f"循环第 {i + 1} 次执行失败: {result.message}",
                            step.step_id
                        )
                    
                    # 检查图像
                    image_result = self.screen_capture.find_image(
                        image_path,
                        threshold=threshold,
                        region=region
                    )
                    
                    # 判断是否满足条件
                    if (until_found and image_result) or (not until_found and not image_result):
                        return ScriptExecutionResult(
                            True,
                            f"循环条件满足，共执行 {i + 1} 次",
                            step.step_id
                        )
                
                return ScriptExecutionResult(
                    False,
                    f"达到最大循环次数 {max_iterations}，条件未满足",
                    step.step_id
                )
            
            elif loop_type == "until_text":
                # 直到文本出现/消失循环
                text = loop_params.get("text", "")
                lang = loop_params.get("lang", "eng")
                region = loop_params.get("region")
                until_found = loop_params.get("until_found", True)
                max_iterations = loop_params.get("max_iterations", 10)
                
                # 检查文本
                if not text:
                    return ScriptExecutionResult(False, "未指定要查找的文本", step.step_id)
                
                for i in range(max_iterations):
                    # 检查是否停止执行
                    if not self.executing or self.paused:
                        break
                    
                    # 执行循环步骤
                    result = self._execute_step(loop_step_obj, -1)
                    
                    # 检查步骤执行结果
                    if not result.success:
                        return ScriptExecutionResult(
                            False,
                            f"循环第 {i + 1} 次执行失败: {result.message}",
                            step.step_id
                        )
                    
                    # 检查文本
                    text_result = self.screen_capture.find_text(
                        text,
                        lang=lang,
                        region=region
                    )
                    
                    # 判断是否满足条件
                    if (until_found and text_result) or (not until_found and not text_result):
                        return ScriptExecutionResult(
                            True,
                            f"循环条件满足，共执行 {i + 1} 次",
                            step.step_id
                        )
                
                return ScriptExecutionResult(
                    False,
                    f"达到最大循环次数 {max_iterations}，条件未满足",
                    step.step_id
                )
            
            else:
                return ScriptExecutionResult(False, f"未知循环类型: {loop_type}", step.step_id)
        
        except Exception as e:
            return ScriptExecutionResult(False, f"循环执行失败: {str(e)}", step.step_id)


"""
使用示例：

from core.script import Script, ScriptStep, ScriptStepType, ScriptExecutor

# 创建脚本
script = Script("script1", "测试脚本", "测试脚本描述")

# 添加步骤
script.add_step(ScriptStep("step1", ScriptStepType.CLICK, {"x": 100, "y": 100}, "点击位置"))
script.add_step(ScriptStep("step2", ScriptStepType.WAIT, {"seconds": 1.0}, "等待1秒"))
script.add_step(ScriptStep("step3", ScriptStepType.TYPE, {"text": "Hello World"}, "输入文本"))

# 保存脚本
script.save("test_script.json")

# 加载脚本
loaded_script = Script.load("test_script.json")

# 创建执行器
executor = ScriptExecutor()

# 加载脚本
executor.load_script(loaded_script)

# 执行脚本
def on_step_start(step, index):
    print(f"开始执行步骤 {index + 1}: {step.description}")

def on_step_complete(step, index, result):
    print(f"步骤 {index + 1} 执行完成: {result.message}")

def on_script_complete(success, message):
    print(f"脚本执行完成: {message}")

executor.execute(on_step_start, on_step_complete, on_script_complete)
"""
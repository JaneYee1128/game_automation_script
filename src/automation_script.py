"""
自动化脚本模块
提供高级自动化功能，如条件判断、循环等
"""

import os
import time
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
import pyautogui

from event_player import EventPlayer
from event_recorder import EventRecorder
from image_recognition import ImageRecognition
from screen_capture import ScreenCapture
from config import config

logger = logging.getLogger('AutomationScript')

class AutomationScript:
    """自动化脚本类，提供高级自动化功能"""
    
    def __init__(self):
        """初始化自动化脚本"""
        self.player = EventPlayer()
        self.recorder = EventRecorder()
        self.image_recognition = ImageRecognition()
        self.screen_capture = ScreenCapture()
        
        # 脚本数据
        self.script_data = {
            "name": "",
            "description": "",
            "version": "1.0",
            "steps": []
        }
        
        # 脚本执行状态
        self.running = False
        self.paused = False
        self.current_step = 0
        self.variables = {}  # 脚本变量
        self.loop_counters = {}  # 循环计数器
        
        # 回调函数
        self.on_step_start = None
        self.on_step_end = None
        self.on_script_end = None
    
    def load_script(self, file_path: str) -> bool:
        """
        加载自动化脚本
        
        参数:
            file_path: 脚本文件路径
        
        返回:
            bool: 是否成功加载
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.script_data = json.load(f)
            logger.info(f"已加载脚本: {self.script_data['name']}")
            return True
        except Exception as e:
            logger.error(f"加载脚本失败: {str(e)}")
            return False
    
    def save_script(self, file_path: str) -> bool:
        """
        保存自动化脚本
        
        参数:
            file_path: 脚本文件路径
        
        返回:
            bool: 是否成功保存
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.script_data, f, indent=2)
            logger.info(f"已保存脚本到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存脚本失败: {str(e)}")
            return False
    
    def add_step(self, step_type: str, **kwargs) -> int:
        """
        添加脚本步骤
        
        参数:
            step_type: 步骤类型
            **kwargs: 步骤参数
        
        返回:
            int: 步骤索引
        """
        step = {
            "type": step_type,
            "enabled": True,
            **kwargs
        }
        self.script_data["steps"].append(step)
        return len(self.script_data["steps"]) - 1
    
    def run_script(self, from_step: int = 0) -> bool:
        """
        运行自动化脚本
        
        参数:
            from_step: 从哪一步开始运行
        
        返回:
            bool: 是否成功完成
        """
        if not self.script_data["steps"]:
            logger.error("脚本为空，无法运行")
            return False
        
        self.running = True
        self.paused = False
        self.current_step = from_step
        self.variables = {}
        self.loop_counters = {}
        
        logger.info(f"开始运行脚本: {self.script_data['name']}")
        
        try:
            while self.running and self.current_step < len(self.script_data["steps"]):
                # 检查是否暂停
                while self.paused and self.running:
                    time.sleep(0.1)
                
                if not self.running:
                    break
                
                # 获取当前步骤
                step = self.script_data["steps"][self.current_step]
                
                # 如果步骤被禁用，跳过
                if not step.get("enabled", True):
                    self.current_step += 1
                    continue
                
                # 执行步骤前回调
                if self.on_step_start:
                    self.on_step_start(self.current_step, step)
                
                # 执行步骤
                logger.info(f"执行步骤 {self.current_step + 1}/{len(self.script_data['steps'])}: {step['type']}")
                success = self._execute_step(step)
                
                # 执行步骤后回调
                if self.on_step_end:
                    self.on_step_end(self.current_step, step, success)
                
                # 根据执行结果决定下一步
                if success:
                    # 如果有指定下一步，跳转到指定步骤
                    if "next_step" in step and step["next_step"] is not None:
                        self.current_step = step["next_step"]
                    else:
                        self.current_step += 1
                else:
                    # 如果执行失败且有指定失败步骤，跳转到失败步骤
                    if "on_failure" in step and step["on_failure"] is not None:
                        self.current_step = step["on_failure"]
                    else:
                        self.current_step += 1
            
            logger.info("脚本执行完成")
            
            # 脚本结束回调
            if self.on_script_end:
                self.on_script_end(True)
            
            return True
        except Exception as e:
            logger.error(f"脚本执行出错: {str(e)}")
            
            # 脚本结束回调
            if self.on_script_end:
                self.on_script_end(False)
            
            return False
        finally:
            self.running = False
    
    def stop_script(self) -> None:
        """停止脚本执行"""
        self.running = False
        logger.info("脚本执行已停止")
    
    def pause_script(self) -> None:
        """暂停脚本执行"""
        self.paused = True
        logger.info("脚本执行已暂停")
    
    def resume_script(self) -> None:
        """恢复脚本执行"""
        self.paused = False
        logger.info("脚本执行已恢复")
    
    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """
        执行单个脚本步骤
        
        参数:
            step: 步骤数据
        
        返回:
            bool: 是否成功执行
        """
        step_type = step["type"]
        
        # 基本步骤类型
        if step_type == "click":
            return self._execute_click(step)
        elif step_type == "double_click":
            return self._execute_double_click(step)
        elif step_type == "right_click":
            return self._execute_right_click(step)
        elif step_type == "move":
            return self._execute_move(step)
        elif step_type == "drag":
            return self._execute_drag(step)
        elif step_type == "key":
            return self._execute_key(step)
        elif step_type == "text":
            return self._execute_text(step)
        elif step_type == "wait":
            return self._execute_wait(step)
        elif step_type == "find_image":
            return self._execute_find_image(step)
        elif step_type == "find_text":
            return self._execute_find_text(step)
        elif step_type == "condition":
            return self._execute_condition(step)
        elif step_type == "loop":
            return self._execute_loop(step)
        elif step_type == "end_loop":
            return self._execute_end_loop(step)
        elif step_type == "set_variable":
            return self._execute_set_variable(step)
        elif step_type == "play_recording":
            return self._execute_play_recording(step)
        elif step_type == "execute_command":
            return self._execute_command(step)
        elif step_type == "screenshot":
            return self._execute_screenshot(step)
        else:
            logger.error(f"未知的步骤类型: {step_type}")
            return False
    
    def _execute_click(self, step: Dict[str, Any]) -> bool:
        """执行点击步骤"""
        try:
            x = self._resolve_value(step.get("x", 0))
            y = self._resolve_value(step.get("y", 0))
            button = step.get("button", "left")
            duration = step.get("duration", 0.1)
            
            logger.debug(f"点击位置: ({x}, {y}), 按钮: {button}")
            pyautogui.click(x=x, y=y, button=button, duration=duration)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行点击步骤失败: {str(e)}")
            return False
    
    def _execute_double_click(self, step: Dict[str, Any]) -> bool:
        """执行双击步骤"""
        try:
            x = self._resolve_value(step.get("x", 0))
            y = self._resolve_value(step.get("y", 0))
            button = step.get("button", "left")
            duration = step.get("duration", 0.1)
            
            logger.debug(f"双击位置: ({x}, {y}), 按钮: {button}")
            pyautogui.doubleClick(x=x, y=y, button=button, duration=duration)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行双击步骤失败: {str(e)}")
            return False
    
    def _execute_right_click(self, step: Dict[str, Any]) -> bool:
        """执行右键点击步骤"""
        try:
            x = self._resolve_value(step.get("x", 0))
            y = self._resolve_value(step.get("y", 0))
            duration = step.get("duration", 0.1)
            
            logger.debug(f"右键点击位置: ({x}, {y})")
            pyautogui.rightClick(x=x, y=y, duration=duration)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行右键点击步骤失败: {str(e)}")
            return False
    
    def _execute_move(self, step: Dict[str, Any]) -> bool:
        """执行鼠标移动步骤"""
        try:
            x = self._resolve_value(step.get("x", 0))
            y = self._resolve_value(step.get("y", 0))
            duration = step.get("duration", 0.1)
            
            logger.debug(f"移动鼠标到: ({x}, {y})")
            pyautogui.moveTo(x=x, y=y, duration=duration)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行鼠标移动步骤失败: {str(e)}")
            return False
    
    def _execute_drag(self, step: Dict[str, Any]) -> bool:
        """执行拖拽步骤"""
        try:
            x1 = self._resolve_value(step.get("x1", 0))
            y1 = self._resolve_value(step.get("y1", 0))
            x2 = self._resolve_value(step.get("x2", 0))
            y2 = self._resolve_value(step.get("y2", 0))
            duration = step.get("duration", 0.5)
            button = step.get("button", "left")
            
            logger.debug(f"拖拽从 ({x1}, {y1}) 到 ({x2}, {y2})")
            pyautogui.moveTo(x=x1, y=y1)
            pyautogui.dragTo(x=x2, y=y2, duration=duration, button=button)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行拖拽步骤失败: {str(e)}")
            return False
    
    def _execute_key(self, step: Dict[str, Any]) -> bool:
        """执行按键步骤"""
        try:
            key = step.get("key", "")
            if not key:
                logger.error("按键步骤缺少key参数")
                return False
            
            # 处理组合键
            if isinstance(key, list):
                logger.debug(f"按下组合键: {'+'.join(key)}")
                pyautogui.hotkey(*key)
            else:
                logger.debug(f"按下按键: {key}")
                pyautogui.press(key)
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行按键步骤失败: {str(e)}")
            return False
    
    def _execute_text(self, step: Dict[str, Any]) -> bool:
        """执行输入文本步骤"""
        try:
            text = step.get("text", "")
            if not text:
                logger.error("输入文本步骤缺少text参数")
                return False
            
            # 解析变量
            text = self._resolve_value(text)
            
            logger.debug(f"输入文本: {text}")
            pyautogui.write(text, interval=step.get("interval", 0.05))
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行输入文本步骤失败: {str(e)}")
            return False
    
    def _execute_wait(self, step: Dict[str, Any]) -> bool:
        """执行等待步骤"""
        try:
            duration = self._resolve_value(step.get("duration", 1.0))
            logger.debug(f"等待 {duration} 秒")
            time.sleep(duration)
            return True
        except Exception as e:
            logger.error(f"执行等待步骤失败: {str(e)}")
            return False
    
    def _execute_play_recording(self, step: Dict[str, Any]) -> bool:
        """执行回放录制步骤"""
        try:
            file_name = step.get("file", "")
            if not file_name:
                logger.error("回放录制步骤缺少file参数")
                return False
            
            # 解析变量
            file_name = self._resolve_value(file_name)
            
            # 构建完整路径
            if not os.path.isabs(file_name):
                file_name = os.path.join(config.recordings_path, file_name)
            
            if not os.path.exists(file_name):
                logger.error(f"录制文件不存在: {file_name}")
                return False
            
            # 设置回放参数
            speed = step.get("speed", config.default_speed)
            
            # 加载并回放录制
            if self.player.load_recording(file_name):
                logger.debug(f"开始回放录制: {file_name}")
                self.player.start_playback(speed=speed)
                
                # 等待回放完成
                while self.player.playing:
                    time.sleep(0.1)
                    if not self.running:
                        self.player.stop_playback()
                        break
                
                # 等待指定时间
                if "wait_after" in step:
                    time.sleep(step["wait_after"])
                
                return True
            else:
                logger.error(f"加载录制文件失败: {file_name}")
                return False
        except Exception as e:
            logger.error(f"执行回放录制步骤失败: {str(e)}")
            return False
    
    def _execute_screenshot(self, step: Dict[str, Any]) -> bool:
        """执行截图步骤"""
        try:
            file_name = step.get("file", f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png")
            region = step.get("region", None)
            
            # 解析变量
            file_name = self._resolve_value(file_name)
            
            # 构建完整路径
            if not os.path.isabs(file_name):
                file_name = os.path.join(config.get("paths.screenshots", "screenshots"), file_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            
            # 捕获屏幕
            screenshot = self.screen_capture.capture(region)
            
            # 保存截图
            screenshot.save(file_name)
            logger.debug(f"保存截图到: {file_name}")
            
            # 保存路径到变量
            if "save_to" in step:
                var_name = step["save_to"]
                self.variables[var_name] = file_name
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return True
        except Exception as e:
            logger.error(f"执行截图步骤失败: {str(e)}")
            return False
    
    def _execute_find_image(self, step: Dict[str, Any]) -> bool:
        """执行查找图像步骤"""
        try:
            image_path = step.get("image_path", "")
            if not image_path:
                logger.error("查找图像步骤缺少image_path参数")
                return False
            
            # 确保图像路径存在
            if not os.path.isabs(image_path):
                image_path = os.path.join(config.templates_path, image_path)
            
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return False
            
            # 捕获屏幕
            screenshot = self.screen_capture.capture()
            
            # 设置匹配参数
            confidence = step.get("confidence", config.match_threshold)
            region = step.get("region", None)
            
            # 查找图像
            result = self.image_recognition.find_template(screenshot, image_path, confidence, region)
            
            if result:
                logger.debug(f"找到图像 {image_path} 在位置 {result}")
                
                # 保存结果到变量
                if "save_to" in step:
                    var_name = step["save_to"]
                    self.variables[var_name] = result
                
                # 如果需要点击
                if step.get("click", False):
                    x, y = result[0] + result[2] // 2, result[1] + result[3] // 2
                    pyautogui.click(x=x, y=y)
                    logger.debug(f"点击找到的图像位置: ({x}, {y})")
                
                # 等待指定时间
                if "wait_after" in step:
                    time.sleep(step["wait_after"])
                
                return True
            else:
                logger.debug(f"未找到图像: {image_path}")
                return False
        except Exception as e:
            logger.error(f"执行查找图像步骤失败: {str(e)}")
            return False
    
    def _execute_find_text(self, step: Dict[str, Any]) -> bool:
        """执行查找文本步骤"""
        try:
            text = step.get("text", "")
            if not text:
                logger.error("查找文本步骤缺少text参数")
                return False
            
            # 解析变量
            text = self._resolve_value(text)
            
            # 捕获屏幕
            screenshot = self.screen_capture.capture()
            
            # 设置匹配参数
            region = step.get("region", None)
            
            # 查找文本
            result = self.image_recognition.find_text(screenshot, text, region)
            
            if result:
                logger.debug(f"找到文本 '{text}' 在位置 {result}")
                
                # 保存结果到变量
                if "save_to" in step:
                    var_name = step["save_to"]
                    self.variables[var_name] = result
                
                # 如果需要点击
                if step.get("click", False):
                    x, y = result[0] + result[2] // 2, result[1] + result[3] // 2
                    pyautogui.click(x=x, y=y)
                    logger.debug(f"点击找到的文本位置: ({x}, {y})")
                
                # 等待指定时间
                if "wait_after" in step:
                    time.sleep(step["wait_after"])
                
                return True
            else:
                logger.debug(f"未找到文本: '{text}'")
                return False
        except Exception as e:
            logger.error(f"执行查找文本步骤失败: {str(e)}")
            return False
    
    def _execute_command(self, step: Dict[str, Any]) -> bool:
        """执行系统命令步骤"""
        try:
            command = step.get("command", "")
            if not command:
                logger.error("执行命令步骤缺少command参数")
                return False
            
            # 解析变量
            command = self._resolve_value(command)
            
            logger.debug(f"执行命令: {command}")
            
            # 执行命令
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # 保存结果到变量
            if "save_to" in step:
                var_name = step["save_to"]
                self.variables[var_name] = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            
            # 等待指定时间
            if "wait_after" in step:
                time.sleep(step["wait_after"])
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"执行命令步骤失败: {str(e)}")
            return False
    
    def _execute_set_variable(self, step: Dict[str, Any]) -> bool:
        """执行设置变量步骤"""
        try:
            var_name = step.get("name", "")
            value = step.get("value", None)
            
            if not var_name:
                logger.error("设置变量步骤缺少name参数")
                return False
            
            # 解析变量值
            resolved_value = self._resolve_value(value)
            
            # 设置变量
            self.variables[var_name] = resolved_value
            logger.debug(f"设置变量 {var_name} = {resolved_value}")
            
            return True
        except Exception as e:
            logger.error(f"执行设置变量步骤失败: {str(e)}")
            return False
    
    def _execute_condition(self, step: Dict[str, Any]) -> bool:
        """执行条件判断步骤"""
        try:
            condition_type = step.get("condition_type", "")
            if not condition_type:
                logger.error("条件判断步骤缺少condition_type参数")
                return False
            
            result = False
            
            if condition_type == "image_exists":
                result = self._check_image_condition(step)
            elif condition_type == "text_exists":
                result = self._check_text_condition(step)
            elif condition_type == "variable_equals":
                result = self._check_variable_equals_condition(step)
            elif condition_type == "variable_contains":
                result = self._check_variable_contains_condition(step)
            else:
                logger.error(f"未知的条件类型: {condition_type}")
                return False
            
            # 根据条件结果决定下一步
            if result:
                logger.debug("条件判断结果: 真")
                if "then_step" in step:
                    self.current_step = step["then_step"] - 1  # 减1是因为每次循环后会加1
            else:
                logger.debug("条件判断结果: 假")
                if "else_step" in step:
                    self.current_step = step["else_step"] - 1  # 减1是因为每次循环后会加1
            
            return True
        except Exception as e:
            logger.error(f"执行条件判断步骤失败: {str(e)}")
            return False
    
    def _check_image_condition(self, step: Dict[str, Any]) -> bool:
        """检查图像条件"""
        image_path = step.get("image_path", "")
        if not image_path:
            logger.error("image_exists条件缺少image_path参数")
            return False
        
        # 确保图像路径存在
        if not os.path.isabs(image_path):
            image_path = os.path.join(config.templates_path, image_path)
        
        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在: {image_path}")
            return False
        
        # 捕获屏幕
        screenshot = self.screen_capture.capture()
        
        # 设置匹配参数
        confidence = step.get("confidence", config.match_threshold)
        region = step.get("region", None)
        
        # 查找图像
        match = self.image_recognition.find_template(screenshot, image_path, confidence, region)
        return match is not None
    
    def _check_text_condition(self, step: Dict[str, Any]) -> bool:
        """检查文本条件"""
        text = step.get("text", "")
        if not text:
            logger.error("text_exists条件缺少text参数")
            return False
        
        # 解析变量
        text = self._resolve_value(text)
        
        # 捕获屏幕
        screenshot = self.screen_capture.capture()
        
        # 设置匹配参数
        region = step.get("region", None)
        
        # 查找文本
        match = self.image_recognition.find_text(screenshot, text, region)
        return match is not None
    
    def _check_variable_equals_condition(self, step: Dict[str, Any]) -> bool:
        """检查变量相等条件"""
        var_name = step.get("variable", "")
        value = step.get("value", None)
        
        if not var_name or value is None:
            logger.error("variable_equals条件缺少variable或value参数")
            return False
        
        # 获取变量值
        var_value = self.variables.get(var_name)
        
        # 解析比较值
        compare_value = self._resolve_value(value)
        
        return var_value == compare_value
    
    def _check_variable_contains_condition(self, step: Dict[str, Any]) -> bool:
        """检查变量包含条件"""
        var_name = step.get("variable", "")
        value = step.get("value", None)
        
        if not var_name or value is None:
            logger.error("variable_contains条件缺少variable或value参数")
            return False
        
        # 获取变量值
        var_value = self.variables.get(var_name)
        
        # 解析比较值
        compare_value = self._resolve_value(value)
        
        if isinstance(var_value, (list, tuple)):
            return compare_value in var_value
        elif isinstance(var_value, dict):
            return compare_value in var_value
        elif isinstance(var_value, str):
            return compare_value in var_value
        else:
            return False
    
    def _execute_loop(self, step: Dict[str, Any]) -> bool:
        """执行循环开始步骤"""
        try:
            loop_id = step.get("loop_id", f"loop_{self.current_step}")
            loop_type = step.get("loop_type", "count")
            
            if loop_type == "count":
                return self._execute_count_loop(step, loop_id)
            elif loop_type == "while":
                return self._execute_while_loop(step, loop_id)
            else:
                logger.error(f"未知的循环类型: {loop_type}")
                return False
        except Exception as e:
            logger.error(f"执行循环开始步骤失败: {str(e)}")
            return False
    
    def _execute_count_loop(self, step: Dict[str, Any], loop_id: str) -> bool:
        """执行计数循环"""
        # 计数循环
        count = self._resolve_value(step.get("count", 1))
        
        # 初始化循环计数器
        if loop_id not in self.loop_counters:
            self.loop_counters[loop_id] = {
                "type": "count",
                "current": 0,
                "total": count,
                "start_step": self.current_step
            }
        
        # 检查是否已完成循环
        counter = self.loop_counters[loop_id]
        if counter["current"] >= counter["total"]:
            # 循环结束，跳转到循环结束步骤
            if "end_step" in step:
                self.current_step = step["end_step"]
            
            # 重置循环计数器
            del self.loop_counters[loop_id]
        else:
            # 增加循环计数
            counter["current"] += 1
            logger.debug(f"循环 {loop_id}: {counter['current']}/{counter['total']}")
        
        return True
    
    def _execute_while_loop(self, step: Dict[str, Any], loop_id: str) -> bool:
        """执行while循环"""
        condition_type = step.get("condition_type", "")
        
        if not condition_type:
            logger.error("while循环缺少condition_type参数")
            return False
        
        # 初始化循环信息
        if loop_id not in self.loop_counters:
            self.loop_counters[loop_id] = {
                "type": "while",
                "start_step": self.current_step
            }
        
        # 检查循环条件
        result = False
        
        if condition_type == "image_exists":
            result = self._check_image_condition(step)
        elif condition_type == "variable_equals":
            result = self._check_variable_equals_condition(step)
        
        # 根据条件结果决定是否继续循环
        if not result:
            # 条件不满足，跳转到循环结束步骤
            if "end_step" in step:
                self.current_step = step["end_step"]
            
            # 重置循环信息
            del self.loop_counters[loop_id]
            
            logger.debug(f"while循环 {loop_id} 条件不满足，退出循环")
        
        return True
    
    def _execute_end_loop(self, step: Dict[str, Any]) -> bool:
        """执行循环结束步骤"""
        try:
            loop_id = step.get("loop_id", "")
            
            if not loop_id:
                logger.error("循环结束步骤缺少loop_id参数")
                return False
            
            if loop_id in self.loop_counters:
                counter = self.loop_counters[loop_id]
                
                if counter["type"] == "count":
                    # 检查是否已完成循环
                    if counter["current"] < counter["total"]:
                        # 返回到循环开始
                        self.current_step = counter["start_step"]
                elif counter["type"] == "while":
                    # 返回到循环开始重新检查条件
                    self.current_step = counter["start_step"]
            
            return True
        except Exception as e:
            logger.error(f"执行循环结束步骤失败: {str(e)}")
            return False
    
    def _resolve_value(self, value: Any) -> Any:
        """
        解析值中的变量引用
        支持的格式：
        - ${variable_name} - 直接引用变量
        - ${variable_name.key} - 引用字典变量的键
        - ${variable_name[index]} - 引用列表变量的索引
        """
        if isinstance(value, str):
            import re
            pattern = r'\${([^}]+)}'
            
            def replace_var(match):
                var_path = match.group(1)
                parts = re.split(r'[\.\[]', var_path)
                
                # 获取基础变量
                var_name = parts[0]
                if var_name not in self.variables:
                    return match.group(0)
                
                result = self.variables[var_name]
                
                # 处理后续的键或索引
                for part in parts[1:]:
                    if part.endswith(']'):  # 列表索引
                        try:
                            index = int(part[:-1])
                            result = result[index]
                        except (ValueError, IndexError):
                            return match.group(0)
                    else:  # 字典键
                        try:
                            result = result[part]
                        except (KeyError, TypeError):
                            return match.group(0)
                
                return str(result)
            
            return re.sub(pattern, replace_var, value)
        
        return value

# 示例脚本
EXAMPLE_SCRIPT = {
    "name": "游戏自动化示例",
    "description": "演示各种自动化功能的使用方法",
    "version": "1.0",
    "steps": [
        {
            "type": "set_variable",
            "name": "retry_count",
            "value": 3,
            "description": "设置重试次数变量"
        },
        {
            "type": "loop",
            "loop_id": "main_loop",
            "loop_type": "count",
            "count": "${retry_count}",
            "description": "主循环，尝试多次"
        },
        {
            "type": "find_image",
            "image_path": "start_button.png",
            "confidence": 0.8,
            "click": True,
            "save_to": "button_pos",
            "description": "查找并点击开始按钮"
        },
        {
            "type": "wait",
            "duration": 2.0,
            "description": "等待游戏加载"
        },
        {
            "type": "condition",
            "condition_type": "image_exists",
            "image_path": "game_ready.png",
            "confidence": 0.9,
            "then_step": 6,
            "else_step": 8,
            "description": "检查游戏是否准备就绪"
        },
        {
            "type": "play_recording",
            "file": "game_sequence.json",
            "speed": 1.0,
            "description": "执行预录制的游戏操作序列"
        },
        {
            "type": "screenshot",
            "file": "game_result_${retry_count}.png",
            "description": "保存游戏结果截图"
        },
        {
            "type": "end_loop",
            "loop_id": "main_loop",
            "description": "结束主循环"
        }
    ]
}

"""
使用示例：

# 创建自动化脚本实例
script = AutomationScript()

# 设置回调函数
def on_step_start(step_index, step):
    print(f"开始执行步骤 {step_index + 1}: {step.get('description', step['type'])}")

def on_step_end(step_index, step, success):
    status = "成功" if success else "失败"
    print(f"步骤 {step_index + 1} 执行{status}")

def on_script_end(success):
    print(f"脚本执行{'成功' if success else '失败'}")

script.on_step_start = on_step_start
script.on_step_end = on_step_end
script.on_script_end = on_script_end

# 加载示例脚本
script.script_data = EXAMPLE_SCRIPT

# 运行脚本
script.run_script()
"""
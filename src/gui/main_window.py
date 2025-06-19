"""
主窗口模块
提供游戏自动化脚本系统的图形用户界面
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QTabWidget, QFileDialog, QMessageBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QGroupBox, QFormLayout, QLineEdit,
    QSplitter, QMenu, QAction, QToolBar, QStatusBar, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap

# 导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
from automation_script import AutomationScript
from event_recorder import EventRecorder
from event_player import EventPlayer
from screen_capture import ScreenCapture
from image_recognition import ImageRecognition
from logger import logger_setup

# 设置日志
logger = logger_setup.get_logger('GUI')

class RecordingThread(QThread):
    """录制线程"""
    
    # 信号
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, recorder: EventRecorder, output_file: str):
        """
        初始化录制线程
        
        参数:
            recorder: 事件录制器
            output_file: 输出文件路径
        """
        super().__init__()
        self.recorder = recorder
        self.output_file = output_file
    
    def run(self):
        """运行线程"""
        try:
            # 开始录制
            self.recorder.start_recording()
            self.status_signal.emit("正在录制...")
            
            # 等待录制结束
            while self.recorder.recording:
                time.sleep(0.1)
            
            # 保存录制
            success = self.recorder.save_recording(self.output_file)
            
            if success:
                self.status_signal.emit(f"已保存录制到: {self.output_file}")
            else:
                self.status_signal.emit("保存录制失败")
            
            self.finished_signal.emit(success)
        except Exception as e:
            logger.error(f"录制线程出错: {str(e)}")
            self.status_signal.emit(f"录制出错: {str(e)}")
            self.finished_signal.emit(False)

class PlaybackThread(QThread):
    """回放线程"""
    
    # 信号
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)  # 当前事件索引, 总事件数
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, player: EventPlayer, recording_file: str, speed: float = 1.0):
        """
        初始化回放线程
        
        参数:
            player: 事件播放器
            recording_file: 录制文件路径
            speed: 回放速度
        """
        super().__init__()
        self.player = player
        self.recording_file = recording_file
        self.speed = speed
    
    def run(self):
        """运行线程"""
        try:
            # 加载录制文件
            if not self.player.load_recording(self.recording_file):
                self.status_signal.emit(f"加载录制文件失败: {self.recording_file}")
                self.finished_signal.emit(False)
                return
            
            # 设置事件回调
            total_events = len(self.player.events)
            
            def on_event(index, event, success):
                self.progress_signal.emit(index + 1, total_events)
            
            self.player.on_event = on_event
            
            # 开始回放
            self.player.start_playback(speed=self.speed)
            self.status_signal.emit("正在回放...")
            
            # 等待回放结束
            while self.player.playing:
                time.sleep(0.1)
            
            self.status_signal.emit("回放已完成")
            self.finished_signal.emit(True)
        except Exception as e:
            logger.error(f"回放线程出错: {str(e)}")
            self.status_signal.emit(f"回放出错: {str(e)}")
            self.finished_signal.emit(False)

class ScriptThread(QThread):
    """脚本执行线程"""
    
    # 信号
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)  # 当前步骤索引, 总步骤数
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, script: AutomationScript, script_data: Dict[str, Any]):
        """
        初始化脚本执行线程
        
        参数:
            script: 自动化脚本执行器
            script_data: 脚本数据
        """
        super().__init__()
        self.script = script
        self.script_data = script_data
    
    def run(self):
        """运行线程"""
        try:
            # 设置脚本数据
            self.script.script_data = self.script_data
            
            # 设置回调函数
            total_steps = len(self.script_data.get("steps", []))
            
            def on_step_start(step_index, step):
                description = step.get("description", step["type"])
                self.status_signal.emit(f"执行步骤 {step_index + 1}: {description}")
                self.progress_signal.emit(step_index + 1, total_steps)
            
            def on_step_end(step_index, step, success):
                status = "成功" if success else "失败"
                description = step.get("description", step["type"])
                self.status_signal.emit(f"步骤 {step_index + 1} ({description}) 执行{status}")
            
            def on_script_end(success):
                status = "成功" if success else "失败"
                self.status_signal.emit(f"脚本执行{status}")
                self.finished_signal.emit(success)
            
            self.script.on_step_start = on_step_start
            self.script.on_step_end = on_step_end
            self.script.on_script_end = on_script_end
            
            # 运行脚本
            self.script.run_script()
        except Exception as e:
            logger.error(f"脚本执行线程出错: {str(e)}")
            self.status_signal.emit(f"脚本执行出错: {str(e)}")
            self.finished_signal.emit(False)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("游戏自动化脚本系统")
        self.resize(1000, 700)
        
        # 创建组件
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
        
        # 初始化模块
        self.recorder = EventRecorder()
        self.player = EventPlayer()
        self.script = AutomationScript()
        self.capture = ScreenCapture()
        self.recognition = ImageRecognition()
        
        # 设置录制回调
        self.recorder.on_start = lambda: self.status_bar.showMessage("开始录制")
        self.recorder.on_stop = lambda: self.status_bar.showMessage("停止录制")
        
        # 设置回放回调
        self.player.on_start = lambda: self.status_bar.showMessage("开始回放")
        self.player.on_stop = lambda: self.status_bar.showMessage("停止回放")
        
        # 线程
        self.recording_thread = None
        self.playback_thread = None
        self.script_thread = None
        
        # 当前脚本数据
        self.current_script_data = None
        self.current_script_file = None
        
        # 当前录制文件
        self.current_recording_file = None
        
        # 更新状态
        self._update_status()
        
        logger.info("GUI已初始化")
    
    def _create_actions(self):
        """创建动作"""
        # 文件菜单动作
        self.new_script_action = QAction("新建脚本", self)
        self.new_script_action.setShortcut("Ctrl+N")
        self.new_script_action.triggered.connect(self._new_script)
        
        self.open_script_action = QAction("打开脚本", self)
        self.open_script_action.setShortcut("Ctrl+O")
        self.open_script_action.triggered.connect(self._open_script)
        
        self.save_script_action = QAction("保存脚本", self)
        self.save_script_action.setShortcut("Ctrl+S")
        self.save_script_action.triggered.connect(self._save_script)
        
        self.save_script_as_action = QAction("脚本另存为", self)
        self.save_script_as_action.setShortcut("Ctrl+Shift+S")
        self.save_script_as_action.triggered.connect(self._save_script_as)
        
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # 录制菜单动作
        self.start_recording_action = QAction("开始录制", self)
        self.start_recording_action.triggered.connect(self._start_recording)
        
        self.stop_recording_action = QAction("停止录制", self)
        self.stop_recording_action.triggered.connect(self._stop_recording)
        self.stop_recording_action.setEnabled(False)
        
        self.open_recording_action = QAction("打开录制文件", self)
        self.open_recording_action.triggered.connect(self._open_recording)
        
        # 回放菜单动作
        self.start_playback_action = QAction("开始回放", self)
        self.start_playback_action.triggered.connect(self._start_playback)
        self.start_playback_action.setEnabled(False)
        
        self.stop_playback_action = QAction("停止回放", self)
        self.stop_playback_action.triggered.connect(self._stop_playback)
        self.stop_playback_action.setEnabled(False)
        
        # 工具菜单动作
        self.take_screenshot_action = QAction("截图", self)
        self.take_screenshot_action.triggered.connect(self._take_screenshot)
        
        self.find_image_action = QAction("查找图像", self)
        self.find_image_action.triggered.connect(self._find_image)
        
        self.find_text_action = QAction("查找文本", self)
        self.find_text_action.triggered.connect(self._find_text)
        
        self.list_windows_action = QAction("列出窗口", self)
        self.list_windows_action.triggered.connect(self._list_windows)
        
        # 设置菜单动作
        self.preferences_action = QAction("首选项", self)
        self.preferences_action.triggered.connect(self._show_preferences)
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction(self.new_script_action)
        file_menu.addAction(self.open_script_action)
        file_menu.addAction(self.save_script_action)
        file_menu.addAction(self.save_script_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 录制菜单
        recording_menu = menu_bar.addMenu("录制")
        recording_menu.addAction(self.start_recording_action)
        recording_menu.addAction(self.stop_recording_action)
        recording_menu.addSeparator()
        recording_menu.addAction(self.open_recording_action)
        
        # 回放菜单
        playback_menu = menu_bar.addMenu("回放")
        playback_menu.addAction(self.start_playback_action)
        playback_menu.addAction(self.stop_playback_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu("工具")
        tools_menu.addAction(self.take_screenshot_action)
        tools_menu.addAction(self.find_image_action)
        tools_menu.addAction(self.find_text_action)
        tools_menu.addAction(self.list_windows_action)
        
        # 设置菜单
        settings_menu = menu_bar.addMenu("设置")
        settings_menu.addAction(self.preferences_action)
    
    def _create_tool_bar(self):
        """创建工具栏"""
        tool_bar = QToolBar("主工具栏")
        tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(tool_bar)
        
        # 添加动作
        tool_bar.addAction(self.new_script_action)
        tool_bar.addAction(self.open_script_action)
        tool_bar.addAction(self.save_script_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.start_recording_action)
        tool_bar.addAction(self.stop_recording_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.start_playback_action)
        tool_bar.addAction(self.stop_playback_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.take_screenshot_action)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _create_central_widget(self):
        """创建中央部件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 创建脚本列表
        script_group = QGroupBox("脚本步骤")
        script_layout = QVBoxLayout(script_group)
        
        self.script_list = QListWidget()
        script_layout.addWidget(self.script_list)
        
        # 创建步骤操作按钮
        step_buttons_layout = QHBoxLayout()
        
        add_step_button = QPushButton("添加步骤")
        add_step_button.clicked.connect(self._add_step)
        step_buttons_layout.addWidget(add_step_button)
        
        edit_step_button = QPushButton("编辑步骤")
        edit_step_button.clicked.connect(self._edit_step)
        step_buttons_layout.addWidget(edit_step_button)
        
        remove_step_button = QPushButton("删除步骤")
        remove_step_button.clicked.connect(self._remove_step)
        step_buttons_layout.addWidget(remove_step_button)
        
        script_layout.addLayout(step_buttons_layout)
        left_layout.addWidget(script_group)
        
        # 创建右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 创建脚本控制面板
        control_group = QGroupBox("脚本控制")
        control_layout = QVBoxLayout(control_group)
        
        # 创建控制按钮
        control_buttons_layout = QHBoxLayout()
        
        run_script_button = QPushButton("运行脚本")
        run_script_button.clicked.connect(self._run_script)
        control_buttons_layout.addWidget(run_script_button)
        
        stop_script_button = QPushButton("停止脚本")
        stop_script_button.clicked.connect(self._stop_script)
        control_buttons_layout.addWidget(stop_script_button)
        
        control_layout.addLayout(control_buttons_layout)
        
        # 创建日志输出
        log_label = QLabel("日志输出:")
        control_layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        control_layout.addWidget(self.log_output)
        
        right_layout.addWidget(control_group)
        
        # 添加面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # 设置分割器初始大小
        splitter.setSizes([300, 700])
    
    def _update_status(self):
        """更新状态"""
        # 更新动作状态
        is_recording = self.recorder.recording if hasattr(self, 'recorder') else False
        is_playing = self.player.playing if hasattr(self, 'player') else False
        
        self.start_recording_action.setEnabled(not is_recording and not is_playing)
        self.stop_recording_action.setEnabled(is_recording)
        self.start_playback_action.setEnabled(not is_recording and not is_playing and self.current_recording_file is not None)
        self.stop_playback_action.setEnabled(is_playing)
    
    def _new_script(self):
        """新建脚本"""
        if self.current_script_data and self._check_save_changes():
            return
        
        self.current_script_data = {
            "name": "新建脚本",
            "description": "这是一个新建的自动化脚本",
            "version": "1.0",
            "steps": []
        }
        self.current_script_file = None
        
        self._update_script_list()
        self.status_bar.showMessage("已创建新脚本")
    
    def _open_script(self):
        """打开脚本"""
        if self.current_script_data and self._check_save_changes():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开脚本",
            config.get("paths.scripts", "scripts"),
            "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_script_data = json.load(f)
                self.current_script_file = file_path
                
                self._update_script_list()
                self.status_bar.showMessage(f"已打开脚本: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开脚本失败: {str(e)}")
    
    def _save_script(self):
        """保存脚本"""
        if not self.current_script_data:
            return
        
        if not self.current_script_file:
            return self._save_script_as()
        
        try:
            with open(self.current_script_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_script_data, f, indent=2)
            
            self.status_bar.showMessage(f"已保存脚本: {self.current_script_file}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存脚本失败: {str(e)}")
            return False
    
    def _save_script_as(self):
        """脚本另存为"""
        if not self.current_script_data:
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存脚本",
            config.get("paths.scripts", "scripts"),
            "JSON文件 (*.json)"
        )
        
        if file_path:
            self.current_script_file = file_path
            return self._save_script()
        
        return False
    
    def _check_save_changes(self):
        """检查是否需要保存更改"""
        if not self.current_script_data:
            return False
        
        reply = QMessageBox.question(
            self,
            "保存更改",
            "是否保存对当前脚本的更改？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Save:
            return not self._save_script()
        elif reply == QMessageBox.Cancel:
            return True
        
        return False
    
    def _update_script_list(self):
        """更新脚本列表"""
        self.script_list.clear()
        
        if not self.current_script_data:
            return
        
        for i, step in enumerate(self.current_script_data.get("steps", [])):
            description = step.get("description", step["type"])
            item = QListWidgetItem(f"{i+1}. {description}")
            item.setData(Qt.UserRole, step)
            self.script_list.addItem(item)
    
    def _add_step(self):
        """添加步骤"""
        # TODO: 实现添加步骤对话框
        pass
    
    def _edit_step(self):
        """编辑步骤"""
        # TODO: 实现编辑步骤对话框
        pass
    
    def _remove_step(self):
        """删除步骤"""
        current_item = self.script_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self,
            "删除步骤",
            "确定要删除选中的步骤吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.script_list.row(current_item)
            self.script_list.takeItem(row)
            self.current_script_data["steps"].pop(row)
    
    def _run_script(self):
        """运行脚本"""
        if not self.current_script_data:
            QMessageBox.warning(self, "警告", "没有可运行的脚本")
            return
        
        if self.script_thread and self.script_thread.isRunning():
            QMessageBox.warning(self, "警告", "脚本正在运行")
            return
        
        # 创建并启动脚本线程
        self.script_thread = ScriptThread(self.script, self.current_script_data)
        
        self.script_thread.status_signal.connect(
            lambda msg: self.log_output.append(msg)
        )
        
        self.script_thread.progress_signal.connect(
            lambda current, total: self.status_bar.showMessage(f"执行步骤 {current}/{total}")
        )
        
        self.script_thread.finished_signal.connect(
            lambda success: self._on_script_finished(success)
        )
        
        self.script_thread.start()
    
    def _stop_script(self):
        """停止脚本"""
        if self.script_thread and self.script_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "停止脚本",
                "确定要停止正在运行的脚本吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.script.stop_script()
    
    def _on_script_finished(self, success: bool):
        """脚本执行完成回调"""
        status = "成功" if success else "失败"
        self.status_bar.showMessage(f"脚本执行{status}")
        
        if not success:
            QMessageBox.warning(self, "警告", "脚本执行失败")
    
    def _start_recording(self):
        """开始录制"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存录制",
            config.recordings_path,
            "JSON文件 (*.json)"
        )
        
        if file_path:
            # 创建并启动录制线程
            self.recording_thread = RecordingThread(self.recorder, file_path)
            
            self.recording_thread.status_signal.connect(
                lambda msg: self.status_bar.showMessage(msg)
            )
            
            self.recording_thread.finished_signal.connect(
                lambda success: self._on_recording_finished(success)
            )
            
            self.recording_thread.start()
            self._update_status()
    
    def _stop_recording(self):
        """停止录制"""
        if self.recorder.recording:
            self.recorder.stop_recording()
            self._update_status()
    
    def _on_recording_finished(self, success: bool):
        """录制完成回调"""
        self._update_status()
        
        if not success:
            QMessageBox.warning(self, "警告", "录制保存失败")
    
    def _open_recording(self):
        """打开录制文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开录制文件",
            config.recordings_path,
            "JSON文件 (*.json)"
        )
        
        if file_path:
            self.current_recording_file = file_path
            self._update_status()
            self.status_bar.showMessage(f"已加载录制文件: {file_path}")
    
    def _start_playback(self):
        """开始回放"""
        if not self.current_recording_file:
            QMessageBox.warning(self, "警告", "没有可回放的录制文件")
            return
        
        # 创建并启动回放线程
        self.playback_thread = PlaybackThread(
            self.player,
            self.current_recording_file,
            speed=1.0  # TODO: 添加速度控制
        )
        
        self.playback_thread.status_signal.connect(
            lambda msg: self.status_bar.showMessage(msg)
        )
        
        self.playback_thread.progress_signal.connect(
            lambda current, total: self.status_bar.showMessage(f"回放进度: {current}/{total}")
        )
        
        self.playback_thread.finished_signal.connect(
            lambda success: self._on_playback_finished(success)
        )
        
        self.playback_thread.start()
        self._update_status()
    
    def _stop_playback(self):
        """停止回放"""
        if self.player.playing:
            self.player.stop_playback()
            self._update_status()
    
    def _on_playback_finished(self, success: bool):
        """回放完成回调"""
        self._update_status()
        
        if not success:
            QMessageBox.warning(self, "警告", "回放失败")
    
    def _take_screenshot(self):
        """截图"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            config.screenshots_path,
            "PNG图像 (*.png)"
        )
        
        if file_path:
            screenshot = self.capture.capture()
            try:
                screenshot.save(file_path)
                self.status_bar.showMessage(f"已保存截图: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存截图失败: {str(e)}")
    
    def _find_image(self):
        """查找图像"""
        # TODO: 实现查找图像对话框
        pass
    
    def _find_text(self):
        """查找文本"""
        # TODO: 实现查找文本对话框
        pass
    
    def _list_windows(self):
        """列出窗口"""
        windows = self.capture.list_windows()
        
        if windows:
            text = "可见窗口:\n\n" + "\n".join(f"{i+1}. {window}" for i, window in enumerate(windows))
        else:
            text = "未找到可见窗口"
        
        QMessageBox.information(self, "窗口列表", text)
    
    def _show_preferences(self):
        """显示首选项"""
        # TODO: 实现首选项对话框
        pass
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.current_script_data and self._check_save_changes():
            event.ignore()
            return
        
        # 停止录制和回放
        if self.recorder.recording:
            self.recorder.stop_recording()
        
        if self.player.playing:
            self.player.stop_playback()
        
        # 停止脚本执行
        if self.script_thread and self.script_thread.isRunning():
            self.script.stop_script()
            self.script_thread.wait()
        
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
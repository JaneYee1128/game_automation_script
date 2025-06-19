"""
用户界面模块
提供图形界面来控制脚本的功能
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import cv2
import numpy as np
from PIL import Image, ImageTk

# 导入其他模块
from screen_capture import ScreenCapture
from image_recognition import ImageRecognition
from event_recorder import EventRecorder
from event_player import EventPlayer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('GUI')


class AutomationGUI:
    """自动化脚本的图形用户界面"""
    
    def __init__(self, root):
        """
        初始化GUI
        
        参数:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("游戏自动化脚本")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 创建组件
        self.screen_capture = ScreenCapture()
        self.image_recognition = ImageRecognition()
        self.event_recorder = EventRecorder()
        self.event_player = EventPlayer()
        
        # 状态变量
        self.is_recording = False
        self.is_playing = False
        self.is_capturing = False
        self.capture_interval = 500  # 屏幕捕获间隔（毫秒）
        
        # 创建UI
        self._create_ui()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 启动屏幕捕获线程
        self.capture_thread = None
        self.stop_capture = threading.Event()
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧和右侧面板
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 控制区域
        self._create_control_panel(left_frame)
        
        # 右侧面板 - 屏幕预览和日志
        self._create_preview_panel(right_frame)
    
    def _create_control_panel(self, parent):
        """创建控制面板"""
        # 创建标签页
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 录制标签页
        record_tab = ttk.Frame(notebook)
        notebook.add(record_tab, text="录制")
        self._create_record_tab(record_tab)
        
        # 回放标签页
        playback_tab = ttk.Frame(notebook)
        notebook.add(playback_tab, text="回放")
        self._create_playback_tab(playback_tab)
        
        # 识别标签页
        recognition_tab = ttk.Frame(notebook)
        notebook.add(recognition_tab, text="识别")
        self._create_recognition_tab(recognition_tab)
        
        # 设置标签页
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="设置")
        self._create_settings_tab(settings_tab)
    
    def _create_record_tab(self, parent):
        """创建录制标签页"""
        # 会话名称
        ttk.Label(parent, text="会话名称:").pack(anchor=tk.W, padx=5, pady=5)
        
        session_frame = ttk.Frame(parent)
        session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.session_name_var = tk.StringVar()
        session_entry = ttk.Entry(session_frame, textvariable=self.session_name_var)
        session_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 录制按钮
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.record_button = ttk.Button(
            button_frame, 
            text="开始录制", 
            command=self._toggle_recording
        )
        self.record_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        save_button = ttk.Button(
            button_frame, 
            text="保存录制", 
            command=self._save_recording
        )
        save_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 录制列表
        ttk.Label(parent, text="录制列表:").pack(anchor=tk.W, padx=5, pady=5)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.recordings_listbox = tk.Listbox(list_frame)
        self.recordings_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.recordings_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recordings_listbox.config(yscrollcommand=scrollbar.set)
        
        # 刷新录制列表
        refresh_button = ttk.Button(
            parent, 
            text="刷新列表", 
            command=self._refresh_recordings_list
        )
        refresh_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 初始加载录制列表
        self._refresh_recordings_list()
    
    def _create_playback_tab(self, parent):
        """创建回放标签页"""
        # 回放控制
        ttk.Label(parent, text="回放控制:").pack(anchor=tk.W, padx=5, pady=5)
        
        # 回放按钮
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_button = ttk.Button(
            button_frame, 
            text="开始回放", 
            command=self._toggle_playback
        )
        self.play_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.pause_button = ttk.Button(
            button_frame, 
            text="暂停", 
            command=self._toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 回放速度
        speed_frame = ttk.Frame(parent)
        speed_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(speed_frame, text="回放速度:").pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(
            speed_frame, 
            from_=0.1, 
            to=5.0, 
            orient=tk.HORIZONTAL, 
            variable=self.speed_var,
            command=self._update_speed_label
        )
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # 录制列表
        ttk.Label(parent, text="可用录制:").pack(anchor=tk.W, padx=5, pady=5)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.playback_listbox = tk.Listbox(list_frame)
        self.playback_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.playback_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playback_listbox.config(yscrollcommand=scrollbar.set)
        
        # 双击选择录制
        self.playback_listbox.bind("<Double-1>", self._on_recording_selected)
        
        # 刷新录制列表
        refresh_button = ttk.Button(
            parent, 
            text="刷新列表", 
            command=self._refresh_playback_list
        )
        refresh_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 初始加载录制列表
        self._refresh_playback_list()
    
    def _create_recognition_tab(self, parent):
        """创建识别标签页"""
        # 模板管理
        ttk.Label(parent, text="模板管理:").pack(anchor=tk.W, padx=5, pady=5)
        
        # 模板操作按钮
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        capture_template_button = ttk.Button(
            button_frame, 
            text="捕获新模板", 
            command=self._capture_template
        )
        capture_template_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        load_template_button = ttk.Button(
            button_frame, 
            text="加载模板", 
            command=self._load_template
        )
        load_template_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 模板列表
        ttk.Label(parent, text="可用模板:").pack(anchor=tk.W, padx=5, pady=5)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.templates_listbox = tk.Listbox(list_frame)
        self.templates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.templates_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.templates_listbox.config(yscrollcommand=scrollbar.set)
        
        # 识别操作
        ttk.Label(parent, text="识别操作:").pack(anchor=tk.W, padx=5, pady=5)
        
        find_button = ttk.Button(
            parent, 
            text="查找选中模板", 
            command=self._find_template
        )
        find_button.pack(fill=tk.X, padx=5, pady=5)
        
        ocr_button = ttk.Button(
            parent, 
            text="识别屏幕文字", 
            command=self._recognize_text
        )
        ocr_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 刷新模板列表
        refresh_button = ttk.Button(
            parent, 
            text="刷新模板列表", 
            command=self._refresh_templates_list
        )
        refresh_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 初始加载模板列表
        self._refresh_templates_list()
    
    def _create_settings_tab(self, parent):
        """创建设置标签页"""
        # 屏幕捕获设置
        ttk.Label(parent, text="屏幕捕获设置:").pack(anchor=tk.W, padx=5, pady=5)
        
        # 捕获间隔
        interval_frame = ttk.Frame(parent)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="捕获间隔 (ms):").pack(side=tk.LEFT, padx=5)
        
        self.interval_var = tk.IntVar(value=self.capture_interval)
        interval_spinbox = ttk.Spinbox(
            interval_frame, 
            from_=100, 
            to=2000, 
            increment=100,
            textvariable=self.interval_var,
            command=self._update_capture_interval
        )
        interval_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 捕获区域
        ttk.Label(parent, text="捕获区域:").pack(anchor=tk.W, padx=5, pady=5)
        
        region_frame = ttk.Frame(parent)
        region_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.full_screen_var = tk.BooleanVar(value=True)
        full_screen_check = ttk.Checkbutton(
            region_frame, 
            text="全屏", 
            variable=self.full_screen_var,
            command=self._toggle_region_inputs
        )
        full_screen_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # 区域输入框
        region_inputs_frame = ttk.Frame(parent)
        region_inputs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X坐标
        ttk.Label(region_inputs_frame, text="X:").grid(row=0, column=0, padx=5, pady=2)
        self.region_x_var = tk.IntVar(value=0)
        region_x_entry = ttk.Entry(region_inputs_frame, textvariable=self.region_x_var, width=10)
        region_x_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Y坐标
        ttk.Label(region_inputs_frame, text="Y:").grid(row=0, column=2, padx=5, pady=2)
        self.region_y_var = tk.IntVar(value=0)
        region_y_entry = ttk.Entry(region_inputs_frame, textvariable=self.region_y_var, width=10)
        region_y_entry.grid(row=0, column=3, padx=5, pady=2)
        
        # 宽度
        ttk.Label(region_inputs_frame, text="宽度:").grid(row=1, column=0, padx=5, pady=2)
        self.region_width_var = tk.IntVar(value=800)
        region_width_entry = ttk.Entry(region_inputs_frame, textvariable=self.region_width_var, width=10)
        region_width_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 高度
        ttk.Label(region_inputs_frame, text="高度:").grid(row=1, column=2, padx=5, pady=2)
        self.region_height_var = tk.IntVar(value=600)
        region_height_entry = ttk.Entry(region_inputs_frame, textvariable=self.region_height_var, width=10)
        region_height_entry.grid(row=1, column=3, padx=5, pady=2)
        
        # 初始禁用区域输入
        self._toggle_region_inputs()
        
        # 保存设置按钮
        save_settings_button = ttk.Button(
            parent, 
            text="保存设置", 
            command=self._save_settings
        )
        save_settings_button.pack(fill=tk.X, padx=5, pady=10)
    
    def _create_preview_panel(self, parent):
        """创建预览面板"""
        # 预览标签
        preview_label = ttk.Label(parent, text="屏幕预览:")
        preview_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(parent, bg="black")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 开始屏幕捕获
        self._start_screen_capture()
    
    def _start_screen_capture(self):
        """启动屏幕捕获线程"""
        if self.capture_thread is None or not self.capture_thread.is_alive():
            self.stop_capture.clear()
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
    
    def _stop_screen_capture(self):
        """停止屏幕捕获线程"""
        self.stop_capture.set()
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join()
    
    def _capture_loop(self):
        """屏幕捕获循环"""
        while not self.stop_capture.is_set():
            try:
                # 获取捕获区域
                if self.full_screen_var.get():
                    screen = self.screen_capture.capture_screen()
                else:
                    region = {
                        "left": self.region_x_var.get(),
                        "top": self.region_y_var.get(),
                        "width": self.region_width_var.get(),
                        "height": self.region_height_var.get()
                    }
                    screen = self.screen_capture.capture_screen(region)
                
                # 调整图像大小以适应预览窗口
                preview_width = self.preview_canvas.winfo_width()
                preview_height = self.preview_canvas.winfo_height()
                
                if preview_width > 1 and preview_height > 1:  # 确保窗口已经创建
                    # 计算缩放比例
                    scale = min(
                        preview_width / screen.shape[1],
                        preview_height / screen.shape[0]
                    )
                    
                    # 缩放图像
                    width = int(screen.shape[1] * scale)
                    height = int(screen.shape[0] * scale)
                    resized = cv2.resize(screen, (width, height))
                    
                    # 转换为PhotoImage
                    image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    photo = ImageTk.PhotoImage(image=image)
                    
                    # 更新预览
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(
                        preview_width // 2,
                        preview_height // 2,
                        image=photo,
                        anchor=tk.CENTER
                    )
                    self.preview_canvas.image = photo  # 保持引用
            
            except Exception as e:
                logger.error(f"屏幕捕获错误: {str(e)}")
            
            # 等待下一次捕获
            time.sleep(self.capture_interval / 1000.0)
    
    def _toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording:
            # 开始录制
            session_name = self.session_name_var.get()
            if not session_name:
                session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.event_recorder.start_recording(session_name):
                self.is_recording = True
                self.record_button.config(text="停止录制")
                logger.info(f"开始录制: {session_name}")
        else:
            # 停止录制
            if self.event_recorder.stop_recording():
                self.is_recording = False
                self.record_button.config(text="开始录制")
                self._refresh_recordings_list()
                logger.info("停止录制")
    
    def _save_recording(self):
        """保存当前录制"""
        if self.event_recorder.events:
            if self.event_recorder.save_recording():
                self._refresh_recordings_list()
                messagebox.showinfo("成功", "录制已保存")
            else:
                messagebox.showerror("错误", "保存录制失败")
        else:
            messagebox.showwarning("警告", "没有可保存的录制")
    
    def _toggle_playback(self):
        """切换回放状态"""
        if not self.is_playing:
            # 获取选中的录制
            selection = self.playback_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个录制")
                return
            
            recording_name = self.playback_listbox.get(selection[0])
            
            # 开始回放
            if self.event_player.start_playback(recording_name, self.speed_var.get()):
                self.is_playing = True
                self.play_button.config(text="停止回放")
                self.pause_button.config(state=tk.NORMAL)
                logger.info(f"开始回放: {recording_name}")
        else:
            # 停止回放
            if self.event_player.stop_playback():
                self.is_playing = False
                self.play_button.config(text="开始回放")
                self.pause_button.config(state=tk.DISABLED)
                logger.info("停止回放")
    
    def _toggle_pause(self):
        """切换暂停状态"""
        if self.event_player.pause_event.is_set():
            self.event_player.pause_playback()
            self.pause_button.config(text="继续")
        else:
            self.event_player.resume_playback()
            self.pause_button.config(text="暂停")
    
    def _update_speed_label(self, *args):
        """更新速度标签"""
        speed = self.speed_var.get()
        self.speed_label.config(text=f"{speed:.1f}x")
        if self.is_playing:
            self.event_player.set_speed(speed)
    
    def _refresh_recordings_list(self):
        """刷新录制列表"""
        self.recordings_listbox.delete(0, tk.END)
        recordings = self.event_recorder.get_recordings_list()
        for recording in recordings:
            self.recordings_listbox.insert(tk.END, recording)
    
    def _refresh_playback_list(self):
        """刷新回放列表"""
        self.playback_listbox.delete(0, tk.END)
        recordings = self.event_player.get_recordings_list()
        for recording in recordings:
            self.playback_listbox.insert(tk.END, recording)
    
    def _refresh_templates_list(self):
        """刷新模板列表"""
        self.templates_listbox.delete(0, tk.END)
        templates = [name for name in self.image_recognition.templates.keys()]
        for template in templates:
            self.templates_listbox.insert(tk.END, template)
    
    def _on_recording_selected(self, event):
        """处理录制选择事件"""
        selection = self.playback_listbox.curselection()
        if selection:
            recording_name = self.playback_listbox.get(selection[0])
            if self.event_player.load_recording(recording_name):
                logger.info(f"加载录制: {recording_name}")
    
    def _capture_template(self):
        """捕获新模板"""
        # TODO: 实现模板捕获功能
        messagebox.showinfo("提示", "模板捕获功能正在开发中")
    
    def _load_template(self):
        """加载模板文件"""
        filetypes = [
            ("图像文件", "*.png;*.jpg;*.jpeg"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="选择模板图像",
            filetypes=filetypes
        )
        
        if filename:
            template = cv2.imread(filename)
            if template is not None:
                template_name = os.path.splitext(os.path.basename(filename))[0]
                self.image_recognition.add_template(template_name, template)
                self._refresh_templates_list()
                messagebox.showinfo("成功", f"已加载模板: {template_name}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")
    
    def _find_template(self):
        """查找选中的模板"""
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        template_name = self.templates_listbox.get(selection[0])
        screen = self.screen_capture.capture_screen()
        
        locations = self.image_recognition.find_template(screen, template_name)
        
        if locations:
            # 在预览中标记匹配位置
            preview_width = self.preview_canvas.winfo_width()
            preview_height = self.preview_canvas.winfo_height()
            
            scale = min(
                preview_width / screen.shape[1],
                preview_height / screen.shape[0]
            )
            
            for x, y, w, h, conf in locations:
                # 缩放坐标
                scaled_x = int(x * scale)
                scaled_y = int(y * scale)
                scaled_w = int(w * scale)
                scaled_h = int(h * scale)
                
                # 绘制矩形
                self.preview_canvas.create_rectangle(
                    scaled_x,
                    scaled_y,
                    scaled_x + scaled_w,
                    scaled_y + scaled_h,
                    outline="red",
                    width=2
                )
            
            messagebox.showinfo("成功", f"找到 {len(locations)} 个匹配")
        else:
            messagebox.showinfo("提示", "未找到匹配")
    
    def _recognize_text(self):
        """识别屏幕文字"""
        screen = self.screen_capture.capture_screen()
        text = self.image_recognition.recognize_text(screen)
        
        if text:
            # 创建文本显示窗口
            text_window = tk.Toplevel(self.root)
            text_window.title("识别结果")
            text_window.geometry("400x300")
            
            text_widget = tk.Text(text_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            text_widget.insert(tk.END, text)
            text_widget.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("提示", "未识别到文字")
    
    def _toggle_region_inputs(self):
        """切换区域输入状态"""
        state = tk.DISABLED if self.full_screen_var.get() else tk.NORMAL
        for child in self.winfo_children():
            if isinstance(child, ttk.Entry):
                child.config(state=state)
    
    def _update_capture_interval(self):
        """更新捕获间隔"""
        self.capture_interval = self.interval_var.get()
    
    def _save_settings(self):
        """保存设置"""
        # TODO: 实现设置保存功能
        messagebox.showinfo("提示", "设置保存功能正在开发中")
    
    def _on_close(self):
        """关闭窗口时的处理"""
        # 停止录制
        if self.is_recording:
            self.event_recorder.stop_recording()
        
        # 停止回放
        if self.is_playing:
            self.event_player.stop_playback()
        
        # 停止屏幕捕获
        self._stop_screen_capture()
        
        # 销毁窗口
        self.root.destroy()


# 主函数
def main():
    """主函数"""
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
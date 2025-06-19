"""
基础对话框模块
提供一个基础对话框类，作为所有自定义对话框的基类
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

class BaseDialog(QDialog):
    """基础对话框类"""
    
    # 自定义信号
    accepted_signal = pyqtSignal(dict)  # 当对话框被接受时发出，携带数据
    rejected_signal = pyqtSignal()      # 当对话框被拒绝时发出
    
    def __init__(
        self,
        parent=None,
        title="对话框",
        width=400,
        height=300,
        modal=True,
        buttons=QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    ):
        """
        初始化对话框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            width: 对话框宽度
            height: 对话框高度
            modal: 是否为模态对话框
            buttons: 对话框按钮，默认为确定和取消
        """
        super().__init__(parent)
        
        # 设置对话框属性
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setModal(modal)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 创建内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.main_layout.addWidget(self.content_widget)
        
        # 创建按钮区域
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI
        子类应该重写此方法来添加自己的UI元素
        """
        pass
    
    def get_data(self) -> dict:
        """
        获取对话框数据
        子类应该重写此方法来返回对话框收集的数据
        
        返回:
            dict: 对话框数据
        """
        return {}
    
    def validate_data(self) -> bool:
        """
        验证对话框数据
        子类应该重写此方法来验证数据的有效性
        
        返回:
            bool: 数据是否有效
        """
        return True
    
    def accept(self):
        """确定按钮点击处理"""
        if self.validate_data():
            data = self.get_data()
            self.accepted_signal.emit(data)
            super().accept()
    
    def reject(self):
        """取消按钮点击处理"""
        self.rejected_signal.emit()
        super().reject()
    
    def show_error(self, message: str):
        """
        显示错误消息
        
        参数:
            message: 错误消息
        """
        QMessageBox.critical(self, "错误", message)
    
    def show_warning(self, message: str):
        """
        显示警告消息
        
        参数:
            message: 警告消息
        """
        QMessageBox.warning(self, "警告", message)
    
    def show_info(self, message: str):
        """
        显示信息消息
        
        参数:
            message: 信息消息
        """
        QMessageBox.information(self, "信息", message)
    
    def add_widget(self, widget: QWidget):
        """
        添加部件到内容区域
        
        参数:
            widget: 要添加的部件
        """
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """
        添加布局到内容区域
        
        参数:
            layout: 要添加的布局
        """
        self.content_layout.addLayout(layout)
    
    def add_stretch(self):
        """添加弹性空间"""
        self.content_layout.addStretch()
    
    def add_spacing(self, spacing: int):
        """
        添加间距
        
        参数:
            spacing: 间距大小
        """
        self.content_layout.addSpacing(spacing)
    
    def clear_content(self):
        """清空内容区域"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

"""
使用示例：

class MyDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="我的对话框",
            width=500,
            height=400
        )
    
    def _init_ui(self):
        # 添加标签
        label = QLabel("这是一个自定义对话框")
        self.add_widget(label)
        
        # 添加一些控件...
        
        # 添加弹性空间
        self.add_stretch()
    
    def get_data(self):
        # 返回对话框数据
        return {
            "key": "value"
        }
    
    def validate_data(self):
        # 验证数据
        return True

# 使用对话框
dialog = MyDialog()
if dialog.exec_() == QDialog.Accepted:
    print("对话框被接受")
else:
    print("对话框被取消")
"""
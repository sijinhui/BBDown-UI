from PySide6.QtWidgets import QTextEdit, QGroupBox, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os
import pathlib


class OutputArea:
    """输出显示区域管理类"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.output_text = None
        
    def create_output_area(self, layout):
        """创建输出显示区域"""
        output_group = QGroupBox("输出信息")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Monaco", 10))
        self.output_text.textChanged.connect(self.output_text_changed)
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_group)
        
    def output_text_changed(self):
        """输出文本变化时的处理"""
        if self.parent and not self.output_text.toPlainText().strip():
            # 清空时，自动删除调试日志
            self.clean_debug_files()
            
    def clean_debug_files(self):
        """清理调试文件"""
        if not self.parent:
            return
            
        dir_path = pathlib.Path(self.parent.download_options.work_dir.text())
        for file_path in dir_path.glob("debug_*.json"):
            file_path.unlink()
            
    def append_output(self, text):
        """添加输出文本"""
        if self.output_text:
            self.output_text.append(text)
            
    def clear_output(self):
        """清空输出文本"""
        if self.output_text:
            self.output_text.clear()
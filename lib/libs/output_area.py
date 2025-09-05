from PySide6.QtWidgets import QTextEdit, QGroupBox, QVBoxLayout
from PySide6.QtGui import QFont


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
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_group)
            
    def append_output(self, text):
        """添加输出文本"""
        if self.output_text:
            self.output_text.append(text)
            
    def clear_output(self):
        """清空输出文本"""
        if self.output_text:
            self.output_text.clear()
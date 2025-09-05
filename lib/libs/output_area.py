from PySide6.QtWidgets import QTextEdit, QGroupBox, QVBoxLayout, QPushButton, QApplication, QMainWindow
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer, QRect, QEvent, QObject


class OutputArea(QObject):
    """输出显示区域管理类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.output_text = None
        self.scroll_top_button = None

    def create_output_area(self, layout):
        """创建输出显示区域"""
        output_group = QGroupBox("输出信息")
        output_group.setLayout(QVBoxLayout())

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Monaco", 10))
        self.output_text.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)
        output_group.layout().addWidget(self.output_text)

        # 创建滚动到顶部按钮 - 关键：设置父控件为 QTextEdit
        self.scroll_top_button = QPushButton("↑", self.output_text)
        self.scroll_top_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 220);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 255);
            }
        """)
        self.scroll_top_button.setFixedSize(30, 30)
        self.scroll_top_button.clicked.connect(self._scroll_to_top)
        self.scroll_top_button.hide()

        # 安装事件过滤器
        self.output_text.installEventFilter(self)

        layout.addWidget(output_group)

    def append_output(self, text):
        """添加输出文本"""
        if self.output_text:
            self.output_text.append(text)

    def clear_output(self):
        """清空输出文本"""
        if self.output_text:
            self.output_text.clear()
        if self.scroll_top_button:
            self.scroll_top_button.hide()

    def _on_scroll_changed(self):
        """滚动条位置改变时的处理"""
        if not self.output_text or not self.scroll_top_button:
            return

        # 检查是否需要显示滚动到顶部按钮
        scrollbar = self.output_text.verticalScrollBar()
        if scrollbar.value() > 100:  # 滚动超过100像素才显示按钮
            if not self.scroll_top_button.isVisible():
                self.scroll_top_button.show()
                self._position_scroll_button()
        else:
            self.scroll_top_button.hide()

    def _position_scroll_button(self):
        """定位滚动按钮到右下角"""
        if self.scroll_top_button and self.output_text:
            # 获取 QTextEdit 的大小（不包括滚动条）
            text_edit_rect = self.output_text.rect()
            button_size = self.scroll_top_button.size()

            # 计算按钮位置（右下角，留出边距）
            margin = 10
            x = text_edit_rect.width() - button_size.width() - margin
            y = text_edit_rect.height() - button_size.height() - margin

            # 考虑滚动条的宽度
            if self.output_text.verticalScrollBar().isVisible():
                x -= self.output_text.verticalScrollBar().width()

            self.scroll_top_button.move(x, y)
            self.scroll_top_button.raise_()  # 确保按钮在最上层

    def _scroll_to_top(self):
        """滚动到顶部"""
        if self.output_text:
            self.output_text.verticalScrollBar().setValue(0)

    def eventFilter(self, obj, event):
        """事件过滤器，用于处理按钮的悬浮位置"""
        if obj == self.output_text:
            if event.type() == QEvent.Type.Resize:
                # 窗口大小改变时重新定位按钮
                if self.scroll_top_button and self.scroll_top_button.isVisible():
                    QTimer.singleShot(0, self._position_scroll_button)
            elif event.type() == QEvent.Type.Show:
                # 控件显示时定位按钮
                if self.scroll_top_button and self.scroll_top_button.isVisible():
                    QTimer.singleShot(0, self._position_scroll_button)
        return super().eventFilter(obj, event)


# 测试代码
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("悬浮按钮测试")
        self.setGeometry(100, 100, 600, 400)

        # 创建中央部件
        central_widget = QGroupBox()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建输出区域
        self.output_area = OutputArea(self)
        self.output_area.create_output_area(layout)

        # 添加一些测试内容
        for i in range(50):
            self.output_area.append_output(f"这是第 {i + 1} 行测试内容，用于测试滚动功能。")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
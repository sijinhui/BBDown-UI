from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from .shortcut import ShortcutMixin

class ImageViewerDialog(QDialog, ShortcutMixin):
    """图片查看对话框，用于显示原始分辨率的图片"""

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片查看器")
        self.setModal(False)

        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # 获取图片尺寸
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # 创建布局
        layout = QVBoxLayout(self)

        # 创建滚动区域用于显示大图
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 创建标签显示图片
        self.image_label = QLabel()

        # 如果图片尺寸大于屏幕尺寸，按比例缩放以显示完整图片
        if pixmap_width > screen_width or pixmap_height > screen_height:
            # 按比例缩放图片到屏幕大小
            scaled_pixmap = pixmap.scaled(
                screen_width - 50,
                screen_height - 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
            # 调整窗口大小
            self.resize(
                scaled_pixmap.width() + 20,
                min(scaled_pixmap.height() + 100, screen_height),
            )
        else:
            # 否则显示原始尺寸图片
            self.image_label.setPixmap(pixmap)
            # 调整窗口大小
            self.resize(
                min(pixmap_width + 50, screen_width),
                min(pixmap_height + 100, screen_height),
            )

        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setWidget(self.image_label)

        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # 添加快捷键支持 (Command+W on macOS)
        self.setup_shortcuts()

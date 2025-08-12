import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap


class QRCodeDialog(QDialog):
    """二维码展示弹窗"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("二维码登录")
        self.setModal(False)
        self.resize(400, 400)

        layout = QVBoxLayout(self)

        # 说明标签
        self.info_label = QLabel("请使用B站APP扫描二维码登录")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # 二维码图片标签
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.qr_label)

        # 刷新按钮
        self.refresh_button = QPushButton("刷新二维码")
        self.refresh_button.clicked.connect(self.load_qr_code)
        layout.addWidget(self.refresh_button)

        # 定时器定期检查二维码图片
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_qr_code)
        self.timer.start(2000)  # 每2秒刷新一次

        # 初始化加载二维码
        self.load_qr_code()

    def load_qr_code(self):
        """加载并显示二维码图片"""
        qr_path = os.path.join(os.getcwd(), "qrcode.png")
        if os.path.exists(qr_path):
            pixmap = QPixmap(qr_path)
            if not pixmap.isNull():
                # 缩放图片以适应窗口
                pixmap = pixmap.scaled(
                    300,
                    300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.qr_label.setPixmap(pixmap)
            else:
                self.qr_label.setText("二维码图片加载失败")
        else:
            self.qr_label.setText("等待生成二维码...")
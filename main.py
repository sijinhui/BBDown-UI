import sys
import re
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QCheckBox, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QFont, QClipboard, QPixmap


class BBDownUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BBDown UI - 哔哩哔哩下载工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # 创建URL输入区域
        self.create_url_input_area(main_layout)
        
        # 创建下载选项区域
        self.create_download_options_area(main_layout)
        
        # 创建执行按钮区域
        self.create_action_buttons(main_layout)
        
        # 创建输出显示区域
        self.create_output_area(main_layout)
        
        # 初始化进程
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        # 初始化二维码弹窗
        self.qr_dialog = None

        # 初始化剪贴板监听
        self.clipboard = QApplication.clipboard()
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.last_clipboard_text = ""
        self.clipboard_timer.start(1000)  # 每秒检查一次剪贴板

        # 初始化一些自定义默认值
        self.default_file_pattern = "<ownerName>/<ownerName>-<videoTitle>-<bvid>-<pageNumberWithZero>"
        
    def create_url_input_area(self, layout):
        """创建URL输入区域"""
        url_group = QGroupBox("视频地址")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入哔哩哔哩视频地址或BV号，如：https://www.bilibili.com/video/BV1xx411c7mu 或 BV1xx411c7mu")
        url_layout.addWidget(self.url_input)
        
        layout.addWidget(url_group)
        
    def create_download_options_area(self, layout):
        """创建下载选项区域"""
        options_group = QGroupBox("下载选项")
        options_layout = QVBoxLayout(options_group)
        
        # API模式选择
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API模式:"))
        self.api_combo = QComboBox()
        self.api_combo.addItems(["默认", "TV端", "APP端", "国际版"])
        api_layout.addWidget(self.api_combo)
        api_layout.addStretch()
        options_layout.addLayout(api_layout)
        
        # 编码和画质优先级
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("编码优先级:"))
        self.encoding_input = QLineEdit()
        self.encoding_input.setPlaceholderText("hevc,av1,avc")
        quality_layout.addWidget(self.encoding_input)
        
        quality_layout.addWidget(QLabel("画质优先级:"))
        self.dfn_input = QLineEdit()
        self.dfn_input.setPlaceholderText("8K 超高清, 1080P 高码率, HDR 真彩, 杜比视界")
        quality_layout.addWidget(self.dfn_input)
        options_layout.addLayout(quality_layout)
        
        # 下载选项复选框
        checkboxes_layout = QHBoxLayout()
        
        self.use_aria2 = QCheckBox("使用aria2c下载")
        self.interactive = QCheckBox("交互式选择清晰度")
        self.download_danmaku = QCheckBox("下载弹幕")
        self.video_only = QCheckBox("仅下载视频")
        self.audio_only = QCheckBox("仅下载音频")
        
        checkboxes_layout.addWidget(self.use_aria2)
        checkboxes_layout.addWidget(self.interactive)
        checkboxes_layout.addWidget(self.download_danmaku)
        checkboxes_layout.addWidget(self.video_only)
        checkboxes_layout.addWidget(self.audio_only)
        options_layout.addLayout(checkboxes_layout)
        
        # 更多选项复选框
        more_checkboxes_layout = QHBoxLayout()
        
        self.skip_subtitle = QCheckBox("跳过字幕下载")
        self.skip_cover = QCheckBox("跳过封面下载")
        self.debug = QCheckBox("输出调试日志")
        self.show_all = QCheckBox("显示所有分P")
        
        more_checkboxes_layout.addWidget(self.skip_subtitle)
        more_checkboxes_layout.addWidget(self.skip_cover)
        more_checkboxes_layout.addWidget(self.debug)
        more_checkboxes_layout.addWidget(self.show_all)
        options_layout.addLayout(more_checkboxes_layout)
        
        # 文件命名模式
        file_pattern_layout = QHBoxLayout()
        file_pattern_layout.addWidget(QLabel("单P文件命名:"))
        self.file_pattern = QLineEdit()
        self.file_pattern.setPlaceholderText("<ownerName>/<ownerName>-<videoTitle>-<bvid>-<pageNumberWithZero>")
        file_pattern_layout.addWidget(self.file_pattern)
        
        file_pattern_layout.addWidget(QLabel("多P文件命名:"))
        self.multi_file_pattern = QLineEdit()
        self.multi_file_pattern.setPlaceholderText("<videoTitle>/[P<pageNumberWithZero>]<pageTitle>")
        file_pattern_layout.addWidget(self.multi_file_pattern)
        options_layout.addLayout(file_pattern_layout)
        
        # 工作目录选择
        workdir_layout = QHBoxLayout()
        workdir_layout.addWidget(QLabel("工作目录:"))
        self.work_dir = QLineEdit()
        self.work_dir.setPlaceholderText("请选择工作目录")
        workdir_layout.addWidget(self.work_dir)
        
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_directory)
        workdir_layout.addWidget(self.browse_button)
        options_layout.addLayout(workdir_layout)
        
        layout.addWidget(options_group)
        
    def create_action_buttons(self, layout):
        """创建执行按钮区域"""
        buttons_layout = QHBoxLayout()
        
        self.download_button = QPushButton("开始下载")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004477;
            }
        """)
        
        self.info_button = QPushButton("仅解析信息")
        self.info_button.clicked.connect(self.show_info)
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        self.login_button = QPushButton("登录账号")
        self.login_button.clicked.connect(self.login_account)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        
        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.info_button)
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
    def create_output_area(self, layout):
        """创建输出显示区域"""
        output_group = QGroupBox("输出信息")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_group)
        
    def browse_directory(self):
        """浏览目录选择"""
        directory = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if directory:
            self.work_dir.setText(directory)
            
    def build_command(self, info_only=False):
        """构建BBDown命令"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "请输入视频地址或BV号")
            return None
            
        command = ["BBDown", url]
        
        # 添加API模式参数
        api_mode = self.api_combo.currentText()
        if api_mode == "TV端":
            command.append("--use-tv-api")
        elif api_mode == "APP端":
            command.append("--use-app-api")
        elif api_mode == "国际版":
            command.append("--use-intl-api")
            
        # 添加编码和画质优先级
        encoding = self.encoding_input.text().strip()
        if encoding:
            command.extend(["-e", encoding])
            
        dfn = self.dfn_input.text().strip()
        if dfn:
            command.extend(["-q", dfn])
            
        # 添加复选框选项
        if self.use_aria2.isChecked():
            command.append("--use-aria2c")
        if self.interactive.isChecked():
            command.append("-ia")
        if self.download_danmaku.isChecked():
            command.append("-dd")
        if self.video_only.isChecked():
            command.append("--video-only")
        if self.audio_only.isChecked():
            command.append("--audio-only")
        if self.skip_subtitle.isChecked():
            command.append("--skip-subtitle")
        if self.skip_cover.isChecked():
            command.append("--skip-cover")
        if self.debug.isChecked():
            command.append("--debug")
        if self.show_all.isChecked():
            command.append("--show-all")
        if info_only:
            command.append("--only-show-info")
            
        # 添加文件命名模式
        file_pattern = self.file_pattern.text().strip()
        if file_pattern:
            command.extend(["-F", file_pattern])
        else:
            command.extend(["-F", self.default_file_pattern])
            
        multi_file_pattern = self.multi_file_pattern.text().strip()
        if multi_file_pattern:
            command.extend(["-M", multi_file_pattern])
            
        # 添加工作目录
        work_dir = self.work_dir.text().strip()
        if work_dir:
            command.extend(["--work-dir", work_dir])
            
        return command
        
    def start_download(self):
        """开始下载"""
        command = self.build_command()
        if command:
            self.output_text.clear()
            self.output_text.append(f"执行命令: {' '.join(command)}")
            self.process.start(command[0], command[1:])
            self.download_button.setEnabled(False)
            
    def show_info(self):
        """仅显示信息"""
        command = self.build_command(info_only=True)
        if command:
            self.output_text.clear()
            self.output_text.append(f"执行命令: {' '.join(command)}")
            self.process.start(command[0], command[1:])
            self.info_button.setEnabled(False)
            
    def login_account(self):
        """登录账号"""
        self.output_text.clear()
        self.output_text.append("执行命令: BBDown login")
        self.process.start("BBDown", ["login"])
        self.login_button.setEnabled(False)
        
        # 显示二维码弹窗
        self.qr_dialog = QRCodeDialog(self)
        self.qr_dialog.show()
        
    def handle_not_logged_in(self):
        """处理未登录状态"""
        # 弹出提示框询问用户是否要登录
        reply = QMessageBox.question(self, "未登录提示", 
                                   "检测到您尚未登录B站账号，解析可能受到限制。是否立即登录？", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # 中断当前进程
            if self.process and self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
                self.process.waitForFinished()
            
            # 触发登录操作
            self.login_account()
        else:
            # 用户选择不登录，继续当前操作
            pass
        
    def handle_stdout(self):
        """处理标准输出"""
        data = self.process.readAllStandardOutput()
        try:
            stdout = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用系统默认编码
            stdout = bytes(data).decode("gbk", errors="ignore")
        self.output_text.append(stdout)
        
        # 检测未登录提示
        if "未登录B站账号" in stdout:
            self.handle_not_logged_in()
        
    def handle_stderr(self):
        """处理错误输出"""
        data = self.process.readAllStandardError()
        try:
            stderr = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用系统默认编码
            stderr = bytes(data).decode("gbk", errors="ignore")
        self.output_text.append(stderr)
        
        # 检测未登录提示
        if "未登录B站账号" in stderr:
            self.handle_not_logged_in()
        
    def process_finished(self):
        """进程结束处理"""
        self.download_button.setEnabled(True)
        self.info_button.setEnabled(True)
        self.login_button.setEnabled(True)
        self.output_text.append("操作完成")
        
        # 关闭二维码弹窗（如果存在）
        if hasattr(self, 'qr_dialog') and self.qr_dialog:
            self.qr_dialog.close()
            self.qr_dialog = None
    
    def check_clipboard(self):
        """检查剪贴板内容，如果是B站链接则自动填充"""
        clipboard_text = self.clipboard.text()
        
        # 如果剪贴板内容没有变化，则不处理
        if clipboard_text == self.last_clipboard_text:
            return
            
        # 更新上次剪贴板内容
        self.last_clipboard_text = clipboard_text
        
        # 检查是否为B站链接或BV号
        if self.is_bilibili_url(clipboard_text) and not self.url_input.text():
            self.url_input.setText(clipboard_text)
    
    def is_bilibili_url(self, text):
        """判断文本是否为B站链接或BV号"""
        if not text:
            return False
            
        # B站链接的正则表达式（包括多种可能的URL格式）
        bilibili_patterns = [
            r'https?://(www\.)?bilibili\.com/video/BV\w+',
            r'https?://b23\.tv/\w+',
            r'^BV\w+$'
        ]
        
        # 检查是否匹配B站链接或BV号格式
        for pattern in bilibili_patterns:
            if re.match(pattern, text):
                return True
        return False


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
                pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                self.qr_label.setPixmap(pixmap)
            else:
                self.qr_label.setText("二维码图片加载失败")
        else:
            self.qr_label.setText("等待生成二维码...")


def main():
    app = QApplication(sys.argv)
    window = BBDownUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

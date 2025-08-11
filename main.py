import sys
import re
import os
import yaml
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QCheckBox, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QDialog, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, QProcess, QTimer, QUrl, Slot
from PySide6.QtGui import QFont, QClipboard, QPixmap, QPainter
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from io import BytesIO

# 导入ImageViewerDialog类
from lib.image_viewer import ImageViewerDialog

class ElidedLabel(QLabel):
    """自定义标签类，用于显示截断文本并在鼠标悬停时显示完整文本"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.setWordWrap(True)
        
    def setText(self, text):
        """设置文本内容"""
        self.full_text = text
        super().setText(text)
        
    def resizeEvent(self, event):
        """重写resizeEvent以处理文本截断"""
        super().resizeEvent(event)
        self.elide_text()
        
    def elide_text(self):
        """截断文本并设置tooltip"""
        if not self.full_text:
            return
            
        # 获取标签的可用宽度
        width = self.width() - 20  # 减去一些边距
        if width <= 0:
            return
            
        # 使用字体度量来计算文本宽度
        font_metrics = self.fontMetrics()
        elided_text = font_metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, width)
        super().setText(elided_text)
        
        # 设置完整文本为tooltip
        self.setToolTip(self.full_text)


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
        
        # 创建视频信息横幅区域
        self.create_video_info_banner(main_layout)
        # 用于下载封面图片
        self.net_manager = QNetworkAccessManager(self)  # 必须保存为成员变量，防止被回收

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
        # 初始化基本信息json
        self.if_record_response = False
        self._base_video_info_json = None
        # 保存原始图片数据
        self.original_pixmap = None

        # 初始化剪贴板监听
        self.clipboard = QApplication.clipboard()
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.last_clipboard_text = ""
        self.clipboard_timer.start(1000)  # 每秒检查一次剪贴板

        # 初始化一些自定义默认值
        self.default_file_pattern = "<ownerName>/<ownerName>-<videoTitle>-<bvid>"
        
        # 初始化配置文件路径
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        
        # 加载配置
        self.load_config()
        
        # 连接窗口关闭事件
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
    def create_url_input_area(self, layout):
        """创建URL输入区域"""
        url_group = QGroupBox("视频地址")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入哔哩哔哩视频地址或BV号，如：https://www.bilibili.com/video/BV1xx411c7mu 或 BV1xx411c7mu")
        url_layout.addWidget(self.url_input)
        
        layout.addWidget(url_group)
        
    def create_video_info_banner(self, layout):
        """创建视频信息横幅区域"""
        self.video_info_group = QGroupBox("视频信息")
        video_info_layout = QHBoxLayout(self.video_info_group)
        
        # 视频封面
        self.video_cover_label = QLabel()
        self.video_cover_label.setFixedSize(120, 80)
        self.video_cover_label.setStyleSheet("background-color: transparent; border: none;")
        self.video_cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_cover_label.setText("封面")
        video_info_layout.addWidget(self.video_cover_label)
        
        # 视频信息
        video_text_layout = QVBoxLayout()
        self.video_title_label = QLabel("标题: ")
        self.video_author_label = QLabel("作者: ")
        self.video_desc_label = ElidedLabel("描述: ")
        self.video_title_label.setWordWrap(True)
        self.video_author_label.setWordWrap(True)
        # ElidedLabel已经设置了WordWrap

        video_text_layout.addWidget(self.video_title_label)
        video_text_layout.addWidget(self.video_author_label)
        video_text_layout.addWidget(self.video_desc_label)
        video_info_layout.addLayout(video_text_layout)
        
        # 初始隐藏横幅
        self.video_info_group.setVisible(True)
        layout.addWidget(self.video_info_group)

    @property
    def base_video_info_json(self):
        """获取视频基本信息"""
        return self._base_video_info_json

    @base_video_info_json.setter
    def base_video_info_json(self, value):
        """设置基本信息，并更新对应的框"""
        self._base_video_info_json = value
        pic = value.get("data", {}).get("pic", "")
        author = value.get("data", {}).get("owner", {}).get("name", "")
        title = value.get("data", {}).get("title", "")
        description = value.get("data", {}).get("desc", "")
        self.video_title_label.setText(f"标题: {title}")
        self.video_author_label.setText(f"作者: {author}")
        # 使用ElidedLabel的setText方法设置文本和tooltip
        self.video_desc_label.setText(f"描述: {description}")
        self.set_cover_image(pic)

    def set_cover_image(self, image_url: str):
        request = QNetworkRequest(QUrl(image_url))
        reply = self.net_manager.get(request)
        reply.finished.connect(lambda: self.on_image_downloaded(reply))

    @Slot()
    def on_image_downloaded(self, reply):
        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            # 保存原始图片数据
            self.original_pixmap = pixmap
            
            # 使用KeepAspectRatioByExpanding模式更好地填充标签区域
            pixmap = pixmap.scaled(self.video_cover_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            # 如果图片尺寸大于标签尺寸，则居中裁剪
            if pixmap.width() > self.video_cover_label.width() or pixmap.height() > self.video_cover_label.height():
                x = max(0, (pixmap.width() - self.video_cover_label.width()) // 2)
                y = max(0, (pixmap.height() - self.video_cover_label.height()) // 2)
                pixmap = pixmap.copy(x, y, self.video_cover_label.width(), self.video_cover_label.height())
            self.video_cover_label.setPixmap(pixmap)
            self.video_cover_label.setText("")
            
            # 为封面标签添加点击事件
            self.video_cover_label.mousePressEvent = self.show_full_image
        else:
            self.video_cover_label.setText("加载失败")
        reply.deleteLater()
        
    def show_full_image(self, event):
        """显示原始分辨率的图片"""
        if self.original_pixmap:
            # 创建图片查看对话框并显示
            dialog = ImageViewerDialog(self.original_pixmap, self)
            dialog.show()

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
        self.debug.setChecked(True)
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
        self.file_pattern.setPlaceholderText("<ownerName>/<ownerName>-<videoTitle>-<bvid>")
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
        self.output_text.setFont(QFont("Monaco", 10))
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
            
        # 转换新版个人空间合集链接为旧版格式
        converted_url = self.convert_space_url(url)
        
        command = ["BBDown", converted_url]
        
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
            
    def capture_api_response(self, text):
        """捕获API响应信息"""
        # 查找包含指定URL的行
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "https://api.bilibili.com/x/web-interface/view" in line:
                self.if_record_response = True
                continue
            keyword = "Response: "
            if self.if_record_response and keyword in line:
                response_line = line.strip().split(keyword)[-1]
                try:
                    response_json = json.loads(response_line)
                except Exception as e:
                    print('解析json失败')
                else:
                    self.base_video_info_json = response_json
                    # print(self.base_info_json)
                self.if_record_response = False
        
    def _handle_process_output(self, data, is_stderr=False):
        """处理进程输出的通用方法"""
        try:
            output = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用系统默认编码
            output = bytes(data).decode("gbk", errors="ignore")
        self.output_text.append(output)
        
        # 检测未登录提示
        if "未登录B站账号" in output:
            self.handle_not_logged_in()
            
        # 捕捉API响应信息
        self.capture_api_response(output)
        
    def handle_stdout(self):
        """处理标准输出"""
        data = self.process.readAllStandardOutput()
        self._handle_process_output(data)
        
    def handle_stderr(self):
        """处理错误输出"""
        data = self.process.readAllStandardError()
        self._handle_process_output(data, is_stderr=True)
        
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
    
    def closeEvent(self, event):
        """窗口关闭事件，保存配置"""
        self.save_config()
        event.accept()
    
    def check_clipboard(self):
        """检查剪贴板内容，如果是B站链接则自动填充"""
        clipboard_text = self.clipboard.text()
        
        # 如果剪贴板内容没有变化，则不处理
        if clipboard_text == self.last_clipboard_text:
            return
            
        # 更新上次剪贴板内容
        self.last_clipboard_text = clipboard_text
        
        # 检查是否为B站链接或BV号
        if self.is_bilibili_url(clipboard_text):
            # 转换新版个人空间合集链接为旧版格式
            converted_url = self.convert_space_url(clipboard_text)
            self.url_input.setText(converted_url)
    
    def is_bilibili_url(self, text):
        """判断文本是否为B站链接或BV号"""
        if not text:
            return False
            
        # B站链接的正则表达式（包括多种可能的URL格式）
        bilibili_patterns = [
            r'https?://(www\.)?bilibili\.com/video/BV\w+',
            r'https://space.bilibili.com/\w+',
            r'https?://b23\.tv/\w+',
            r'^BV\w+$'
        ]
        
        # 检查是否匹配B站链接或BV号格式
        for pattern in bilibili_patterns:
            if re.match(pattern, text):
                return True
        return False
        
    def convert_space_url(self, url):
        """将新版个人空间合集链接转换为旧版格式"""
        # 新版个人空间合集链接格式: 
        # https://space.bilibili.com/392959666/lists/1560264?type=season
        # 旧版个人空间合集链接格式:
        # https://space.bilibili.com/392959666/channel/collectiondetail?sid=1560264
        
        # 匹配新版个人空间合集链接
        new_pattern = r'https://space\.bilibili\.com/(\d+)/lists/(\d+)'
        match = re.match(new_pattern, url)
        
        if match:
            uid = match.group(1)  # 用户ID
            sid = match.group(2)  # 合集ID
            
            # 转换为旧版链接格式
            old_url = f"https://space.bilibili.com/{uid}/channel/collectiondetail?sid={sid}"
            return old_url
        
        # 如果不是新版个人空间合集链接，返回原链接
        return url
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                # 加载URL输入
                if 'url' in config:
                    self.url_input.setText(config['url'])
                
                # 加载API模式
                if 'api_mode' in config:
                    index = self.api_combo.findText(config['api_mode'])
                    if index >= 0:
                        self.api_combo.setCurrentIndex(index)
                
                # 加载编码优先级
                if 'encoding' in config:
                    self.encoding_input.setText(config['encoding'])
                
                # 加载画质优先级
                if 'dfn' in config:
                    self.dfn_input.setText(config['dfn'])
                
                # 加载复选框状态
                if 'use_aria2' in config:
                    self.use_aria2.setChecked(config['use_aria2'])
                if 'interactive' in config:
                    self.interactive.setChecked(config['interactive'])
                if 'download_danmaku' in config:
                    self.download_danmaku.setChecked(config['download_danmaku'])
                if 'video_only' in config:
                    self.video_only.setChecked(config['video_only'])
                if 'audio_only' in config:
                    self.audio_only.setChecked(config['audio_only'])
                if 'skip_subtitle' in config:
                    self.skip_subtitle.setChecked(config['skip_subtitle'])
                if 'skip_cover' in config:
                    self.skip_cover.setChecked(config['skip_cover'])
                if 'debug' in config:
                    self.debug.setChecked(config['debug'])
                if 'show_all' in config:
                    self.show_all.setChecked(config['show_all'])
                
                # 加载文件命名模式
                if 'file_pattern' in config:
                    self.file_pattern.setText(config['file_pattern'])
                if 'multi_file_pattern' in config:
                    self.multi_file_pattern.setText(config['multi_file_pattern'])
                
                # 加载工作目录
                if 'work_dir' in config:
                    self.work_dir.setText(config['work_dir'])
                    
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            # 'url': self.url_input.text(),
            'api_mode': self.api_combo.currentText(),
            'encoding': self.encoding_input.text(),
            'dfn': self.dfn_input.text(),
            'use_aria2': self.use_aria2.isChecked(),
            'interactive': self.interactive.isChecked(),
            'download_danmaku': self.download_danmaku.isChecked(),
            'video_only': self.video_only.isChecked(),
            'audio_only': self.audio_only.isChecked(),
            'skip_subtitle': self.skip_subtitle.isChecked(),
            'skip_cover': self.skip_cover.isChecked(),
            'debug': self.debug.isChecked(),
            'show_all': self.show_all.isChecked(),
            'file_pattern': self.file_pattern.text(),
            'multi_file_pattern': self.multi_file_pattern.text(),
            'work_dir': self.work_dir.text()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")


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

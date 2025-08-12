import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QFileDialog, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager

# 导入视频信息横幅相关类
from lib.video_info_banner import VideoInfoBanner
# 导入输出区域管理类
from lib.output_area import OutputArea
# 导入下载选项区域管理类
from lib.download_options import DownloadOptionsArea
# 导入命令构建器
from lib.command_builder import CommandBuilder
# 导入URL处理器
from lib.url_handler import URLHandler

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
        
        # 初始化视频信息横幅管理器
        self.video_info_banner = VideoInfoBanner(self)
        
        # 初始化输出区域管理器
        self.output_area = OutputArea(self)
        
        # 初始化下载选项区域管理器
        self.download_options = DownloadOptionsArea(self)
        
        # 初始化命令构建器
        self.command_builder = CommandBuilder(self)
        
        # 初始化URL处理器
        self.url_handler = URLHandler(self)
        
        # 创建URL输入区域
        self.create_url_input_area(main_layout)
        
        # 创建视频信息横幅区域
        self.video_info_banner.create_video_info_banner(main_layout)
        # 用于下载封面图片
        self.net_manager = QNetworkAccessManager(self)  # 必须保存为成员变量，防止被回收

        # 创建下载选项区域
        self.download_options.create_download_options_area(main_layout)
        
        # 创建执行按钮区域
        self.create_action_buttons(main_layout)
        
        # 创建输出显示区域
        self.output_area.create_output_area(main_layout)
        
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

        # 初始化一些自定义默认值
        self.default_file_pattern = "<ownerName>/<ownerName>-<videoTitle>-<bvid>"
        
        # 初始化配置文件路径
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        
        # 加载配置
        self.download_options.load_config(self.config_file)
        
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
        

    @property
    def base_video_info_json(self):
        """获取视频基本信息"""
        return self._base_video_info_json

    @base_video_info_json.setter
    def base_video_info_json(self, value):
        """设置基本信息，并更新对应的框"""
        self._base_video_info_json = value
        self.video_info_banner.update_video_info(value)

    def set_cover_image(self, image_url: str):
        self.video_info_banner.set_cover_image(image_url)

            
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
        

    def browse_directory(self):
        """浏览目录选择"""
        directory = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if directory:
            self.download_options.work_dir.setText(directory)
            
            
    def start_download(self):
        """开始下载"""
        command = self.command_builder.build_command()
        if command:
            self.output_area.clear_output()
            self.output_area.append_output(f"执行命令: {' '.join(command)}")
            self.process.start(command[0], command[1:])
            self.download_button.setEnabled(False)
            
    def show_info(self):
        """仅显示信息"""
        command = self.command_builder.build_command(info_only=True)
        if command:
            self.output_area.clear_output()
            self.output_area.append_output(f"执行命令: {' '.join(command)}")
            self.process.start(command[0], command[1:])
            self.info_button.setEnabled(False)
            
    def login_account(self):
        """登录账号"""
        self.output_area.clear_output()
        self.output_area.append_output("执行命令: BBDown login")
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
        self.output_area.append_output(output)
        
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
        self.output_area.append_output("操作完成")
        
        # 关闭二维码弹窗（如果存在）
        if hasattr(self, 'qr_dialog') and self.qr_dialog:
            self.qr_dialog.close()
            self.qr_dialog = None
    
    def closeEvent(self, event):
        """窗口关闭事件，保存配置"""
        self.output_area.clean_debug_files()
        self.download_options.save_config(self.config_file)
        event.accept()
    
        
            
            
    

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

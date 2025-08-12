import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QDialog,
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

# 导入执行按钮区域管理类
from lib.action_buttons import ActionButtons


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

        # 初始化执行按钮区域管理器
        self.action_buttons = ActionButtons(self)

        # 创建URL输入区域
        self.create_url_input_area(main_layout)

        # 创建视频信息横幅区域
        self.video_info_banner.create_video_info_banner(main_layout)
        # 用于下载封面图片
        self.net_manager = QNetworkAccessManager(self)  # 必须保存为成员变量，防止被回收

        # 创建下载选项区域
        self.download_options.create_download_options_area(main_layout)

        # 创建执行按钮区域
        self.action_buttons.create_action_buttons(main_layout)

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
        self.config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.yaml"
        )

        # 加载配置
        self.download_options.load_config(self.config_file)

        # 连接窗口关闭事件
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def create_url_input_area(self, layout):
        """创建URL输入区域"""
        url_group = QGroupBox("视频地址")
        url_layout = QVBoxLayout(url_group)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "请输入哔哩哔哩视频地址或BV号，如：https://www.bilibili.com/video/BV1xx411c7mu 或 BV1xx411c7mu"
        )
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

    def browse_directory(self):
        """浏览目录选择"""
        directory = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if directory:
            self.download_options.work_dir.setText(directory)

    def capture_api_response(self, text):
        """捕获API响应信息"""
        # 查找包含指定URL的行
        lines = text.split("\n")
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
                    print("解析json失败")
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
            self.action_buttons.handle_not_logged_in()

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
        self.action_buttons.process_finished()

    def closeEvent(self, event):
        """窗口关闭事件，保存配置"""
        self.output_area.clean_debug_files()
        self.download_options.save_config(self.config_file)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = BBDownUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

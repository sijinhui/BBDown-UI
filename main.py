import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
)
from PySide6.QtCore import Qt
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

# 导入进程处理器
from lib.process_handler import ProcessHandler


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

        # 初始化进程处理器
        self.process_handler = ProcessHandler(self)

        # 创建URL输入区域
        self.url_handler.create_url_input_area(main_layout)

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

        # 初始化二维码弹窗
        self.qr_dialog = None
        # 视频基础信息存储
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

    @property
    def base_video_info_json(self):
        """获取视频基本信息"""
        return self._base_video_info_json

    @base_video_info_json.setter
    def base_video_info_json(self, value):
        """设置基本信息，并更新对应的框"""
        self._base_video_info_json = value
        self.video_info_banner.update_video_info(value)

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

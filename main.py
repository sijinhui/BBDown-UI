import sys
import pathlib
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QGroupBox,
    QScrollArea, QLayout,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QNetworkAccessManager

# 导入视频信息横幅相关类
from lib.libs.video_info_banner import VideoInfoBanner
# 导入输出区域管理类
from lib.libs.output_area import OutputArea
# 导入下载选项区域管理类
from lib.bilibili.download_options import DownloadOptionsArea
# 导入YouTube选项区域管理类
from lib.youtube.youtube_options import YouTubeOptionsArea
# 导入命令构建器
from lib.bilibili.command_builder import CommandBuilder
# 导入YouTube命令构建器
from lib.youtube.youtube_command_builder import YouTubeCommandBuilder
# 导入URL处理器
from lib.libs.url_handler import URLHandler
# 导入执行按钮区域管理类
from lib.libs.action_buttons import ActionButtons
# 导入进程处理器
from lib.libs.process_handler import ProcessHandler
# 导入检查器
from lib.bilibili.checker import check_bbdown_path, setup_system_paths


class BBDownUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 配置系统路径
        setup_system_paths()
        
        self.setWindowTitle("BBDown UI - 哔哩哔哩下载工具")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(":/bilibili.ico"))

        # 初始化下载模式
        self._mode = "bilibili" # "youtube"
        # 初始化二维码弹窗
        self.qr_dialog = None
        # 视频基础信息存储
        self._base_video_info_json = None
        # 初始化一些自定义默认值
        self.default_bilibili_file_pattern = "<ownerName>/<ownerName>-<videoTitle>-<bvid>"
        self.default_youtube_file_pattern = "%(uploader)s/%(title)s [%(id)s].%(ext)s"

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 创建上部区域（输入区+信息卡）
        top_widget = QWidget()
        main_layout.addWidget(top_widget)

        # 创建下部工作区域
        work_widget = QWidget()
        main_layout.addWidget(work_widget)

        # 创建上部区域布局
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        top_layout.setSpacing(8)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 创建工作区域布局
        work_layout = QHBoxLayout(work_widget)
        work_layout.setSpacing(8)
        work_layout.setContentsMargins(0, 0, 0, 0)

        # 创建水平分割器（工作区内的分割器）
        work_splitter = QSplitter(Qt.Orientation.Horizontal)
        work_layout.addWidget(work_splitter)

        # 创建左侧区域（下载选项）
        # left_widget = QScrollArea()
        # left_widget.setWidgetResizable(True)
        left_content = QWidget()
        work_splitter.addWidget(left_content)

        # 创建右侧区域（输出日志）
        right_widget = QScrollArea()
        right_widget.setWidgetResizable(True)
        right_content = QWidget()
        right_widget.setWidget(right_content)
        work_splitter.addWidget(right_widget)

        # 创建左侧区域布局
        left_layout = QVBoxLayout(left_content)
        left_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(6, 6, 6, 6)

        # 创建右侧区域布局
        right_layout = QVBoxLayout(right_content)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(6, 6, 6, 6)

        # 初始化视频信息横幅管理器
        self.video_info_banner = VideoInfoBanner(self)

        # 初始化输出区域管理器
        self.output_area = OutputArea(self)

        # 初始化下载选项区域管理器
        self.download_options = DownloadOptionsArea(self)
        # 初始化YouTube选项区域管理器
        self.youtube_options = YouTubeOptionsArea(self)

        # 初始化命令构建器
        self.command_builder = CommandBuilder(self)
        # 初始化YouTube命令构建器
        self.youtube_command_builder = YouTubeCommandBuilder(self)

        # 初始化URL处理器
        self.url_handler = URLHandler(self)

        # 初始化执行按钮区域管理器
        self.action_buttons = ActionButtons(self)

        # 初始化进程处理器
        self.process_handler = ProcessHandler(self)

        # 创建URL输入区域和按钮区域
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        # 创建URL输入区域，使其占据最大空间
        self.url_handler.create_url_input_area(url_layout)
        # 创建执行按钮区域
        self.action_buttons.create_action_buttons(url_layout)
        top_layout.addLayout(url_layout)
        
        # 创建视频信息布局
        self.video_info_banner.create_video_info_banner(top_layout)

        # 用于下载封面图片
        self.net_manager = QNetworkAccessManager(self)  # 必须保存为成员变量，防止被回收

        # 创建下载选项区域
        self.download_options.create_download_options_area(left_layout)
        # 创建YouTube选项区域
        self.youtube_options.create_youtube_options_area(left_layout)
        left_layout.addStretch()

        # 创建输出显示区域（使用QGroupBox包装）
        output_group = QGroupBox()
        right_layout.addWidget(output_group)
        
        # 创建输出显示布局
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(8)
        output_layout.setContentsMargins(6, 6, 6, 6)
        self.output_area.create_output_area(output_layout)

        # 设置分割器的初始大小
        work_splitter.setSizes([300, 500])
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")

        # 初始化配置文件路径
        self.config_file = str(pathlib.Path.home() / ".BBDown.yaml")

        # 加载配置
        self.download_options.load_config(self.config_file)
        # 加载YouTube配置
        self.youtube_options.load_config(self.config_file)

        # 连接窗口关闭事件
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    @property
    def mode(self):
        return self._mode
    @mode.setter
    def mode(self, value):
        """当模式修改时，对应调整布局"""
        if value == self._mode: return
        self._mode = value
        # 根据值调整布局
        self.update_download_options_layout()
        
    def update_download_options_layout(self):
        """根据模式更新下载选项布局"""
        # 先隐藏所有下载选项卡
        if hasattr(self, 'download_options') and self.download_options:
            self.download_options.options_group.setVisible(self._mode == "bilibili")
        if hasattr(self, 'youtube_options') and self.youtube_options:
            self.youtube_options.options_group.setVisible(self._mode == "youtube")

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
        self.download_options.save_config(self.config_file)
        self.youtube_options.save_config(self.config_file)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BBDown")
    app.setWindowIcon(QIcon(":/bilibili.ico"))
    window = BBDownUI()
    # 检查BBDown路径
    check_bbdown_path(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

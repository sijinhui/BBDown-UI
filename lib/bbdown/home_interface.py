# coding: utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import ScrollArea

from ..libs.url_handler import URLHandler
from ..libs.action_buttons import ActionButtons
from ..bilibili.download_options import DownloadOptionsArea
from ..youtube.youtube_options import YouTubeOptionsArea
from ..libs.output_area import OutputArea
# 导入视频信息卡片
from .video_info_card import VideoInfoCard


class HomeInterface(ScrollArea):
    """主页界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("homeInterface")

        # 初始化组件
        self.video_info_card = VideoInfoCard()
        self.url_handler = URLHandler(parent)
        self.action_buttons = ActionButtons(parent)
        self.download_options = DownloadOptionsArea(parent)
        self.youtube_options = YouTubeOptionsArea(parent)
        self.output_area = OutputArea(parent)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 10)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.__initWidget()

    def __initWidget(self):
        """初始化界面组件"""
        self.enableTransparentBackground()

        # 创建主布局
        self.__initLayout()

    def __initLayout(self):
        """初始化布局"""
        # 视频信息卡片
        self.vBoxLayout.addWidget(self.video_info_card, 0, Qt.AlignmentFlag.AlignTop)

        # URL输入区域
        url_widget = QWidget()
        url_layout = QHBoxLayout(url_widget)
        url_layout.setContentsMargins(0, 0, 0, 0)
        self.url_handler.create_url_input_area(url_layout)
        self.action_buttons.create_action_buttons(url_layout)
        self.vBoxLayout.addWidget(url_widget, 0, Qt.AlignmentFlag.AlignTop)

        # 下载选项区域
        self.vBoxLayout.addWidget(self.download_options, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.youtube_options, 0, Qt.AlignmentFlag.AlignTop)

        # 输出区域
        self.output_area.create_output_area(self.vBoxLayout)

        self.vBoxLayout.addStretch()
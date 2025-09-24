# coding: utf-8
import sys
from typing import List

from PySide6.QtCore import Qt, Signal, QUrl, QSize
from PySide6.QtGui import QIcon, QColor, QDesktopServices
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtSql import QSqlDatabase

from qfluentwidgets import (NavigationItemPosition, MSFluentWindow, SplashScreen, MessageBox,
                           InfoBarIcon, FluentIcon as FIF)

from ..libs.video_info_banner import VideoInfoBanner
from ..libs.output_area import OutputArea
from ..bilibili.download_options import DownloadOptionsArea
from ..youtube.youtube_options import YouTubeOptionsArea
from ..bilibili.command_builder import CommandBuilder
from ..youtube.youtube_command_builder import YouTubeCommandBuilder
from ..libs.url_handler import URLHandler
from ..libs.action_buttons import ActionButtons
from ..libs.process_handler import ProcessHandler
from ..bilibili.checker import check_bbdown_path, setup_system_paths
from ..libs.shortcut import ShortcutMixin
from ..bilibili.fav import BilibiliFav
# 导入界面类
from .home_interface import HomeInterface
from .setting_interface import SettingInterface

class BBDownMainWindow(MSFluentWindow, ShortcutMixin):

    def __init__(self):
        super().__init__()

        # 配置系统路径
        setup_system_paths()
        self.setWindowTitle("BBDown UI - 哔哩哔哩下载工具")
        self.setWindowIcon(QIcon(":/bilibili.ico"))

        self.initWindow()

        # 初始化下载模式
        self._mode = "bilibili"  # "youtube"
        # 初始化二维码弹窗
        self.qr_dialog = None
        # 视频基础信息存储
        self._base_video_info_json = None
        # 初始化一些自定义默认值
        self.default_bilibili_file_pattern = "<ownerName>/<ownerName>-<videoTitle>-<bvid>"
        self.default_youtube_file_pattern = "%(uploader)s/%(title)s [%(id)s].%(ext)s"

        # 初始化界面
        self.homeInterface = HomeInterface(self)
        # self.favInterface = BilibiliFav()
        self.settingInterface = SettingInterface(self)

        # 初始化管理器
        self.video_info_banner = VideoInfoBanner(self)
        self.output_area = OutputArea(self)
        self.download_options = DownloadOptionsArea(self)
        self.youtube_options = YouTubeOptionsArea(self)
        self.command_builder = CommandBuilder(self)
        self.youtube_command_builder = YouTubeCommandBuilder(self)
        self.url_handler = URLHandler(self)
        self.action_buttons = ActionButtons(self)
        self.process_handler = ProcessHandler(self)

        self.connectSignalToSlot()

        # 添加导航项
        self.initNavigation()

        # 检查BBDown路径
        check_bbdown_path(self)

        # 设置快捷键
        self.setup_shortcuts()

    def connectSignalToSlot(self):
        """连接信号到槽函数"""
        pass

    def initNavigation(self):
        """初始化导航"""
        # 添加主页导航项
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'), FIF.HOME_FILL, isTransparent=True)

        # 添加收藏夹导航项
        # self.addSubInterface(self.favInterface, FIF.HEART, self.tr('Favorites'), FIF.HOME_FILL, isTransparent=True)

        # 添加设置导航项到底部
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'),
            FIF.SETTING, NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """初始化窗口"""
        self.resize(1200, 800)
        self.setMinimumWidth(900)

        # 设置背景色
        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(False)

        # 创建启动画面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        # 居中显示
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        """当模式修改时，对应调整布局"""
        if value == self._mode:
            return
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
        # TODO: 修复配置文件路径
        # self.download_options.save_config(self.config_file)
        # self.youtube_options.save_config(self.config_file)
        event.accept()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def onInitFinished(self):
        """初始化完成"""
        self.splashScreen.finish()
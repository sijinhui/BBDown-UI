# coding: utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog
from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup, PushSettingCard,
                           SwitchSettingCard, OptionsSettingCard, HyperlinkCard, PrimaryPushSettingCard,
                           FluentIcon as FIF)
from ..bilibili.checker import setup_system_paths


class SettingInterface(ScrollArea):
    """设置界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 个人化设置组
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)

        # 下载设置组
        self.downloadGroup = SettingCardGroup(
            self.tr('Download'), self.scrollWidget)

        # 关于组
        self.aboutGroup = SettingCardGroup(
            self.tr('About'), self.scrollWidget)

        self.__initWidget()

    def __initWidget(self):
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')
        self.setViewportMargins(0, 90, 0, 20)

        # 初始化布局
        self.__initLayout()

    def __initLayout(self):
        self.expandLayout.setSpacing(26)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        # 添加设置卡片组到布局
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.downloadGroup)
        self.expandLayout.addWidget(self.aboutGroup)

        # 调整图标大小
        from qfluentwidgets import SettingCard
        for card in self.findChildren(SettingCard):
            card.setIconSize(18, 18)
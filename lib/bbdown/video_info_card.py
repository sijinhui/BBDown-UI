# coding:utf-8
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal, QSize, QUrl
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtNetwork import QNetworkRequest

from qfluentwidgets import (BodyLabel, TransparentToolButton, FluentIcon, ElevatedCardWidget,
                            ImageLabel, SimpleCardWidget, HyperlinkLabel, VerticalSeparator,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont)

from lib.libs.image_viewer import ImageViewerDialog


class VideoInfoCard(SimpleCardWidget):
    """ 视频信息卡片 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)
        self.iconLabel = ImageLabel(self)
        self.iconLabel.setFixedSize(120, 80)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.iconLabel.setText("封面")

        self.nameLabel = TitleLabel("视频标题", self)
        self.authorLabel = HyperlinkLabel(QUrl(""), '作者', self)
        self.descriptionLabel = BodyLabel("视频描述", self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()

        self.__initWidgets()

    def __initWidgets(self):
        self.descriptionLabel.setWordWrap(True)
        self.nameLabel.setObjectName("nameLabel")
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.initLayout()

    def initLayout(self):
        self.hBoxLayout.setSpacing(20)
        self.hBoxLayout.setContentsMargins(20, 15, 20, 15)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(5)

        # 名称和作者标签
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addWidget(self.authorLabel, 0, Qt.AlignmentFlag.AlignRight)

        # 描述标签
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addWidget(self.descriptionLabel)

    def update_video_info(self, value, parent, mode):
        """更新视频信息显示"""
        pic = author = title = description = ""
        if mode == "bilibili":
            pic = value.get("data", {}).get("pic", "")
            author = value.get("data", {}).get("owner", {}).get("name", "")
            title = value.get("data", {}).get("title", "")
            description = value.get("data", {}).get("desc", "")
        if mode == "youtube":
            title = value.get("title", "")
            pic = value.get("thumbnail", "")
            description = value.get("description", "")
            author = value.get("uploader", "")

        self.nameLabel.setText(title)
        self.authorLabel.setText(author)
        self.descriptionLabel.setText(description)

        # 设置封面图片
        if pic:
            self.set_cover_image(pic, parent)

    def set_cover_image(self, image_url: str, parent):
        """设置封面图片"""
        request = QNetworkRequest(QUrl(image_url))
        reply = parent.net_manager.get(request)
        reply.finished.connect(lambda: self.on_image_downloaded(reply))

    def on_image_downloaded(self, reply):
        """图片下载完成回调"""
        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            # 使用KeepAspectRatio模式保持图片比例
            pixmap = pixmap.scaled(self.iconLabel.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.iconLabel.setPixmap(pixmap)
            self.iconLabel.setText("")

            # 为封面标签添加点击事件
            self.iconLabel.mousePressEvent = lambda event: self.show_full_image(pixmap)
        else:
            self.iconLabel.setText("加载失败")
        reply.deleteLater()

    def show_full_image(self, pixmap):
        """显示原始分辨率的图片"""
        if pixmap:
            # 创建图片查看对话框并显示
            dialog = ImageViewerDialog(pixmap, self.parent())
            dialog.show()
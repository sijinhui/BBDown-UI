from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLayout
from PySide6.QtCore import Qt, QUrl
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtGui import QPixmap
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


class VideoInfoBanner:
    """视频信息横幅管理类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.video_info_group = None
        self.video_cover_label = None
        self.video_title_label = None
        self.video_author_label = None
        self.video_desc_label = None
        self.original_pixmap = None
        
    def create_video_info_banner(self, layout):
        """创建视频信息横幅区域"""
        self.video_info_group = QGroupBox("视频信息")
        self.video_info_group.setFixedHeight(120)  # 设置固定高度
        video_info_layout = QHBoxLayout(self.video_info_group)
        
        # 视频封面
        video_cover_layout = QVBoxLayout()
        self.video_cover_label = QLabel()
        self.video_cover_label.setFixedSize(120, 80)
        self.video_cover_label.setStyleSheet("background-color: transparent; border: none;")
        self.video_cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_cover_label.setText("封面")
        video_cover_layout.addWidget(self.video_cover_label)
        video_cover_layout.addStretch()
        video_info_layout.addLayout(video_cover_layout)

        # 视频信息
        video_text_layout = QVBoxLayout()
        video_text_layout.setSpacing(12)  # 设置固定间距

        self.video_title_label = QLabel("标题: ")
        self.video_author_label = QLabel("作者: ")
        self.video_desc_label = ElidedLabel("描述: ")
        self.video_title_label.setWordWrap(True)
        self.video_author_label.setWordWrap(True)

        video_text_layout.addWidget(self.video_title_label)
        video_text_layout.addWidget(self.video_author_label)
        video_text_layout.addWidget(self.video_desc_label)
        video_text_layout.addStretch()
        video_info_layout.addLayout(video_text_layout)

        layout.addWidget(self.video_info_group)
        
    def update_video_info(self, value):
        """更新视频信息显示"""
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
        """设置封面图片"""
        request = QNetworkRequest(QUrl(image_url))
        reply = self.parent.net_manager.get(request)
        reply.finished.connect(lambda: self.on_image_downloaded(reply))
        
    def on_image_downloaded(self, reply):
        """图片下载完成回调"""
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
            dialog = ImageViewerDialog(self.original_pixmap, self.parent)
            dialog.show()
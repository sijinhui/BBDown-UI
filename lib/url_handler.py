import re
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLineEdit


class URLHandler:
    def __init__(self, parent):
        self.parent = parent
        self.last_clipboard_text = ""
        
        # 初始化剪贴板监听
        self.clipboard = QApplication.clipboard()
        self.clipboard_timer = QTimer(self.parent)
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.clipboard_timer.start(1000)  # 每秒检查一次剪贴板
        
    def create_url_input_area(self, layout):
        """创建URL输入区域"""
        url_group = QGroupBox("视频地址")
        url_layout = QVBoxLayout(url_group)

        self.parent.url_input = QLineEdit()
        self.parent.url_input.setPlaceholderText(
            "请输入哔哩哔哩视频地址或BV号，如：https://www.bilibili.com/video/BV1xx411c7mu 或 BV1xx411c7mu"
        )
        url_layout.addWidget(self.parent.url_input)
        layout.addWidget(url_group)

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
            self.parent.url_input.setText(converted_url)
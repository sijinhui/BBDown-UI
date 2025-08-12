from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt


class DownloadOptionsArea:
    def __init__(self, parent):
        self.parent = parent
        # 初始化所有需要的控件属性
        self.api_combo = None
        self.encoding_input = None
        self.dfn_input = None
        self.use_aria2 = None
        self.interactive = None
        self.download_danmaku = None
        self.video_only = None
        self.audio_only = None
        self.skip_subtitle = None
        self.skip_cover = None
        self.debug = None
        self.show_all = None
        self.file_pattern = None
        self.multi_file_pattern = None
        self.work_dir = None
        self.browse_button = None

    def create_download_options_area(self, layout):
        """创建下载选项区域"""
        options_group = QGroupBox("下载选项")
        options_layout = QVBoxLayout(options_group)
        
        # API模式选择
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API模式:"))
        self.api_combo = QComboBox()
        self.api_combo.addItems(["默认", "TV端", "APP端", "国际版"])
        api_layout.addWidget(self.api_combo)
        api_layout.addStretch()
        options_layout.addLayout(api_layout)
        
        # 编码和画质优先级
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("编码优先级:"))
        self.encoding_input = QLineEdit()
        self.encoding_input.setPlaceholderText("hevc,av1,avc")
        quality_layout.addWidget(self.encoding_input)
        
        quality_layout.addWidget(QLabel("画质优先级:"))
        self.dfn_input = QLineEdit()
        self.dfn_input.setPlaceholderText("8K 超高清, 1080P 高码率, HDR 真彩, 杜比视界")
        quality_layout.addWidget(self.dfn_input)
        options_layout.addLayout(quality_layout)
        
        # 下载选项复选框
        checkboxes_layout = QHBoxLayout()
        
        self.use_aria2 = QCheckBox("使用aria2c下载")
        self.interactive = QCheckBox("交互式选择清晰度")
        self.download_danmaku = QCheckBox("下载弹幕")
        self.video_only = QCheckBox("仅下载视频")
        self.audio_only = QCheckBox("仅下载音频")
        
        checkboxes_layout.addWidget(self.use_aria2)
        checkboxes_layout.addWidget(self.interactive)
        checkboxes_layout.addWidget(self.download_danmaku)
        checkboxes_layout.addWidget(self.video_only)
        checkboxes_layout.addWidget(self.audio_only)
        options_layout.addLayout(checkboxes_layout)
        
        # 更多选项复选框
        more_checkboxes_layout = QHBoxLayout()
        
        self.skip_subtitle = QCheckBox("跳过字幕下载")
        self.skip_cover = QCheckBox("跳过封面下载")
        self.debug = QCheckBox("输出调试日志")
        self.debug.setChecked(True)
        self.show_all = QCheckBox("显示所有分P")
        
        more_checkboxes_layout.addWidget(self.skip_subtitle)
        more_checkboxes_layout.addWidget(self.skip_cover)
        more_checkboxes_layout.addWidget(self.debug)
        more_checkboxes_layout.addWidget(self.show_all)
        options_layout.addLayout(more_checkboxes_layout)
        
        # 文件命名模式
        file_pattern_layout = QHBoxLayout()
        file_pattern_layout.addWidget(QLabel("单P文件命名:"))
        self.file_pattern = QLineEdit()
        self.file_pattern.setPlaceholderText("<ownerName>/<ownerName>-<videoTitle>-<bvid>")
        file_pattern_layout.addWidget(self.file_pattern)
        
        file_pattern_layout.addWidget(QLabel("多P文件命名:"))
        self.multi_file_pattern = QLineEdit()
        self.multi_file_pattern.setPlaceholderText("<videoTitle>/[P<pageNumberWithZero>]<pageTitle>")
        file_pattern_layout.addWidget(self.multi_file_pattern)
        options_layout.addLayout(file_pattern_layout)
        
        # 工作目录选择
        workdir_layout = QHBoxLayout()
        workdir_layout.addWidget(QLabel("工作目录:"))
        self.work_dir = QLineEdit()
        self.work_dir.setPlaceholderText("请选择工作目录")
        workdir_layout.addWidget(self.work_dir)
        
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.parent.browse_directory)
        workdir_layout.addWidget(self.browse_button)
        options_layout.addLayout(workdir_layout)
        
        layout.addWidget(options_group)
import os
import yaml
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
        self.browse_button.clicked.connect(self.browse_directory)
        workdir_layout.addWidget(self.browse_button)
        options_layout.addLayout(workdir_layout)
        
        layout.addWidget(options_group)
        
    def browse_directory(self):
        """浏览目录选择"""
        from PySide6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(self.parent, "选择工作目录")
        if directory:
            self.work_dir.setText(directory)
            
    def load_config(self, config_file):
        """加载配置文件"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                # 加载URL输入
                if 'url' in config:
                    self.parent.url_input.setText(config['url'])
                
                # 加载API模式
                if 'api_mode' in config:
                    index = self.api_combo.findText(config['api_mode'])
                    if index >= 0:
                        self.api_combo.setCurrentIndex(index)
                
                # 加载编码优先级
                if 'encoding' in config:
                    self.encoding_input.setText(config['encoding'])
                
                # 加载画质优先级
                if 'dfn' in config:
                    self.dfn_input.setText(config['dfn'])
                
                # 加载复选框状态
                if 'use_aria2' in config:
                    self.use_aria2.setChecked(config['use_aria2'])
                if 'interactive' in config:
                    self.interactive.setChecked(config['interactive'])
                if 'download_danmaku' in config:
                    self.download_danmaku.setChecked(config['download_danmaku'])
                if 'video_only' in config:
                    self.video_only.setChecked(config['video_only'])
                if 'audio_only' in config:
                    self.audio_only.setChecked(config['audio_only'])
                if 'skip_subtitle' in config:
                    self.skip_subtitle.setChecked(config['skip_subtitle'])
                if 'skip_cover' in config:
                    self.skip_cover.setChecked(config['skip_cover'])
                if 'debug' in config:
                    self.debug.setChecked(config['debug'])
                if 'show_all' in config:
                    self.show_all.setChecked(config['show_all'])
                
                # 加载文件命名模式
                if 'file_pattern' in config:
                    self.file_pattern.setText(config['file_pattern'])
                if 'multi_file_pattern' in config:
                    self.multi_file_pattern.setText(config['multi_file_pattern'])
                
                # 加载工作目录
                if 'work_dir' in config:
                    self.work_dir.setText(config['work_dir'])
                    
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self, config_file):
        """保存配置到文件"""
        config = {
            # 'url': self.parent.url_input.text(),
            'api_mode': self.api_combo.currentText(),
            'encoding': self.encoding_input.text(),
            'dfn': self.dfn_input.text(),
            'use_aria2': self.use_aria2.isChecked(),
            'interactive': self.interactive.isChecked(),
            'download_danmaku': self.download_danmaku.isChecked(),
            'video_only': self.video_only.isChecked(),
            'audio_only': self.audio_only.isChecked(),
            'skip_subtitle': self.skip_subtitle.isChecked(),
            'skip_cover': self.skip_cover.isChecked(),
            'debug': self.debug.isChecked(),
            'show_all': self.show_all.isChecked(),
            'file_pattern': self.file_pattern.text(),
            'multi_file_pattern': self.multi_file_pattern.text(),
            'work_dir': self.work_dir.text()
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
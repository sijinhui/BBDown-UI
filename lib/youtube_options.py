import os
import yaml
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QLayout
)


class YouTubeOptionsArea:
    def __init__(self, parent):
        self.options_group = None
        self.parent = parent
        # 初始化所有需要的控件属性
        self.format_combo = None
        self.quality_combo = None
        self.audio_format_combo = None
        self.subtitle_checkbox = None
        self.video_only = None
        self.audio_only = None
        self.debug = None
        self.embed_subtitle = None
        self.embed_thumbnail = None
        self.split_chapters = None
        self.file_pattern = None
        self.work_dir = None
        self.browse_button = None

    def create_youtube_options_area(self, layout):
        """创建YouTube下载选项区域"""
        self.options_group = QGroupBox("YouTube下载选项")
        # 默认隐藏
        self.options_group.setVisible(False)
        options_layout = QVBoxLayout(self.options_group)
        
        # 格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["默认", "mp4", "webm", "mkv", "flv", "avi"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # 画质选择
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("画质:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最佳", "8K", "4K", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        options_layout.addLayout(quality_layout)
        
        # 音频格式
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("音频格式:"))
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["最佳", "mp3", "aac", "m4a", "opus", "wav", "flac"])
        audio_layout.addWidget(self.audio_format_combo)
        audio_layout.addStretch()
        options_layout.addLayout(audio_layout)
        
        # 下载选项复选框
        checkboxes_layout = QHBoxLayout()
        
        self.subtitle_checkbox = QCheckBox("下载字幕")
        self.video_only = QCheckBox("仅下载视频")
        self.audio_only = QCheckBox("仅下载音频")
        self.debug = QCheckBox("输出调试日志")
        self.debug.setChecked(False)
        
        checkboxes_layout.addWidget(self.subtitle_checkbox)
        checkboxes_layout.addWidget(self.video_only)
        checkboxes_layout.addWidget(self.audio_only)
        checkboxes_layout.addWidget(self.debug)
        options_layout.addLayout(checkboxes_layout)
        
        # 高级选项复选框
        advanced_checkboxes_layout = QHBoxLayout()
        
        self.embed_subtitle = QCheckBox("嵌入字幕")
        self.embed_thumbnail = QCheckBox("嵌入缩略图")
        self.split_chapters = QCheckBox("分割章节")
        
        advanced_checkboxes_layout.addWidget(self.embed_subtitle)
        advanced_checkboxes_layout.addWidget(self.embed_thumbnail)
        advanced_checkboxes_layout.addWidget(self.split_chapters)
        options_layout.addLayout(advanced_checkboxes_layout)
        
        # 文件命名模式
        file_pattern_layout = QHBoxLayout()
        file_pattern_layout.addWidget(QLabel("文件命名:"))
        self.file_pattern = QLineEdit()
        self.file_pattern.setPlaceholderText("%(title)s-%(id)s.%(ext)s")
        file_pattern_layout.addWidget(self.file_pattern)
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

        options_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.addWidget(self.options_group)
        
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
                    all_config = yaml.safe_load(f) or {}
                config = all_config.get('youtube', {})
                # 加载URL输入
                if 'url' in config:
                    self.parent.url_input.setText(config['url'])
                
                # 加载格式和画质
                if 'youtube_format' in config:
                    index = self.format_combo.findText(config['youtube_format'])
                    if index >= 0:
                        self.format_combo.setCurrentIndex(index)
                
                if 'youtube_quality' in config:
                    index = self.quality_combo.findText(config['youtube_quality'])
                    if index >= 0:
                        self.quality_combo.setCurrentIndex(index)
                
                if 'youtube_audio_format' in config:
                    index = self.audio_format_combo.findText(config['youtube_audio_format'])
                    if index >= 0:
                        self.audio_format_combo.setCurrentIndex(index)
                
                # 加载复选框状态
                if 'youtube_subtitle' in config:
                    self.subtitle_checkbox.setChecked(config['youtube_subtitle'])
                if 'youtube_video_only' in config:
                    self.video_only.setChecked(config['youtube_video_only'])
                if 'youtube_audio_only' in config:
                    self.audio_only.setChecked(config['youtube_audio_only'])
                if 'youtube_debug' in config:
                    self.debug.setChecked(config['youtube_debug'])
                if 'youtube_embed_subtitle' in config:
                    self.embed_subtitle.setChecked(config['youtube_embed_subtitle'])
                if 'youtube_embed_thumbnail' in config:
                    self.embed_thumbnail.setChecked(config['youtube_embed_thumbnail'])
                if 'youtube_split_chapters' in config:
                    self.split_chapters.setChecked(config['youtube_split_chapters'])
                
                # 加载文件命名模式
                if 'youtube_file_pattern' in config:
                    self.file_pattern.setText(config['youtube_file_pattern'])
                
                # 加载工作目录
                if 'youtube_work_dir' in config:
                    self.work_dir.setText(config['youtube_work_dir'])
                    
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self, config_file):
        """保存配置到文件"""
        config = {
            # 'url': self.parent.url_input.text(),
            'youtube_format': self.format_combo.currentText(),
            'youtube_quality': self.quality_combo.currentText(),
            'youtube_audio_format': self.audio_format_combo.currentText(),
            'youtube_subtitle': self.subtitle_checkbox.isChecked(),
            'youtube_video_only': self.video_only.isChecked(),
            'youtube_audio_only': self.audio_only.isChecked(),
            'youtube_debug': self.debug.isChecked(),
            'youtube_embed_subtitle': self.embed_subtitle.isChecked(),
            'youtube_embed_thumbnail': self.embed_thumbnail.isChecked(),
            'youtube_split_chapters': self.split_chapters.isChecked(),
            'youtube_file_pattern': self.file_pattern.text(),
            'youtube_work_dir': self.work_dir.text(),
        }
        
        try:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
            except Exception as e:
                all_config = {}
            all_config['youtube'] = config
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(all_config, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
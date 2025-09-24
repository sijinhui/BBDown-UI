import os
import yaml
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QLayout
)
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from qfluentwidgets import GroupHeaderCardWidget, SwitchButton, IndicatorPosition, LineEdit, ComboBox, CompactSpinBox
from lib.libs.download_dir import downloads_path
from lib.libs.base import OptionsBase

class DownloadOptionsArea(OptionsBase, GroupHeaderCardWidget):
    def __init__(self, parent):
        GroupHeaderCardWidget.__init__(self, parent)
        OptionsBase.__init__(self)

        self.BBDown_PATH = ""
        self.parent = parent
        self.setTitle(self.tr("下载选项"))

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

        self._initWidgets()

    def _initWidgets(self):
        """初始化控件"""
        self.setBorderRadius(8)

        # API模式选择
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API模式:"))
        self.api_combo = ComboBox()
        self.api_combo.addItems(["默认", "TV端", "APP端", "国际版"])
        api_layout.addWidget(self.api_combo)
        api_layout.addStretch()
        api_widget = QWidget()
        api_widget.setLayout(api_layout)
        self.addGroup(":/bilibili.ico", "API设置", "选择API模式", api_widget)

        # 编码和画质优先级
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("编码优先级:"))
        self.encoding_input = LineEdit()
        self.encoding_input.setPlaceholderText("hevc,av1,avc")
        quality_layout.addWidget(self.encoding_input)

        quality_layout.addWidget(QLabel("画质优先级:"))
        self.dfn_input = LineEdit()
        self.dfn_input.setPlaceholderText("8K 超高清, 1080P 高码率, HDR 真彩, 杜比视界")
        quality_layout.addWidget(self.dfn_input)
        quality_widget = QWidget()
        quality_widget.setLayout(quality_layout)
        self.addGroup(":/bilibili.ico", "画质设置", "设置编码和画质优先级", quality_widget)

        # 下载选项开关
        self.use_aria2 = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.use_aria2.setOnText(self.tr("On"))
        self.use_aria2.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "使用aria2c下载", "启用aria2c多线程下载", self.use_aria2)

        self.interactive = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.interactive.setOnText(self.tr("On"))
        self.interactive.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "交互式选择", "交互式选择清晰度", self.interactive)

        self.download_danmaku = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.download_danmaku.setOnText(self.tr("On"))
        self.download_danmaku.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "下载弹幕", "下载视频弹幕", self.download_danmaku)

        self.video_only = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.video_only.setOnText(self.tr("On"))
        self.video_only.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "仅下载视频", "只下载视频流", self.video_only)

        self.audio_only = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.audio_only.setOnText(self.tr("On"))
        self.audio_only.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "仅下载音频", "只下载音频流", self.audio_only)

        # 更多选项开关
        self.skip_subtitle = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.skip_subtitle.setOnText(self.tr("On"))
        self.skip_subtitle.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "跳过字幕", "跳过字幕下载", self.skip_subtitle)

        self.skip_cover = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.skip_cover.setOnText(self.tr("On"))
        self.skip_cover.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "跳过封面", "跳过封面下载", self.skip_cover)

        self.debug = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.debug.setOnText(self.tr("On"))
        self.debug.setOffText(self.tr("Off"))
        self.debug.setChecked(True)
        self.addGroup(":/bilibili.ico", "调试日志", "输出调试日志", self.debug)

        self.show_all = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        self.show_all.setOnText(self.tr("On"))
        self.show_all.setOffText(self.tr("Off"))
        self.addGroup(":/bilibili.ico", "显示所有分P", "显示所有分P视频", self.show_all)

        # 文件命名模式
        file_pattern_layout = QHBoxLayout()
        file_pattern_layout.addWidget(QLabel("单P文件命名:"))
        self.file_pattern = LineEdit()
        self.file_pattern.setPlaceholderText("<ownerName>/<ownerName>-<videoTitle>-<bvid>")
        file_pattern_layout.addWidget(self.file_pattern)
        file_pattern_widget = QWidget()
        file_pattern_widget.setLayout(file_pattern_layout)
        self.addGroup(":/bilibili.ico", "单P文件命名", "设置单P视频文件命名规则", file_pattern_widget)

        file_pattern_layout2 = QHBoxLayout()
        file_pattern_layout2.addWidget(QLabel("多P文件命名:"))
        self.multi_file_pattern = LineEdit()
        self.multi_file_pattern.setPlaceholderText(self.parent.default_bilibili_file_pattern)
        file_pattern_layout2.addWidget(self.multi_file_pattern)
        file_pattern_widget2 = QWidget()
        file_pattern_widget2.setLayout(file_pattern_layout2)
        self.addGroup(":/bilibili.ico", "多P文件命名", "设置多P视频文件命名规则", file_pattern_widget2)

        # 工作目录选择
        workdir_layout = QHBoxLayout()
        workdir_layout.addWidget(QLabel("工作目录:"))
        self.work_dir = LineEdit()
        self.work_dir.setPlaceholderText("请选择工作目录")
        workdir_layout.addWidget(self.work_dir)

        open_button = QPushButton("打开")
        open_button.clicked.connect(self.open_directory)
        workdir_layout.addWidget(open_button)

        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_directory)
        workdir_layout.addWidget(self.browse_button)
        workdir_widget = QWidget()
        workdir_widget.setLayout(workdir_layout)
        self.addGroup(":/bilibili.ico", "工作目录", "设置下载工作目录", workdir_widget)

    def create_download_options_area(self, layout):
        """创建下载选项区域"""
        layout.addWidget(self)

            
    def load_config(self, config_file):
        """加载配置文件"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                config = all_config.get('bilibili', {})
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
                if config.get("work_dir"):
                    self.work_dir.setText(config['work_dir'])
                else:
                    # 添加默认工作目录为当前用户的下载文件夹
                    self.work_dir.setText(str(downloads_path))

                # 程序路径
                if config.get("BBDown_PATH"):
                    self.BBDown_PATH = config.get("BBDown_PATH", "")
                    
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
            'work_dir': self.work_dir.text(),
            'BBDown_PATH': self.BBDown_PATH,
        }
        
        try:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
            except Exception as e:
                all_config = {}
            all_config['bilibili'] = config
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(all_config, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
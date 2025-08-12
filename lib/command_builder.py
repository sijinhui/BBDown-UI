import os
import yaml
from PySide6.QtWidgets import QMessageBox


class CommandBuilder:
    def __init__(self, parent):
        self.parent = parent

    def build_command(self, info_only=False):
        """构建BBDown命令"""
        url = self.parent.url_input.text().strip()
        if not url:
            QMessageBox.warning(self.parent, "警告", "请输入视频地址或BV号")
            return None
            
        # 转换新版个人空间合集链接为旧版格式
        converted_url = self.parent.convert_space_url(url)
        
        command = ["BBDown", converted_url]
        
        # 添加API模式参数
        api_mode = self.parent.download_options.api_combo.currentText()
        if api_mode == "TV端":
            command.append("--use-tv-api")
        elif api_mode == "APP端":
            command.append("--use-app-api")
        elif api_mode == "国际版":
            command.append("--use-intl-api")
            
        # 添加编码和画质优先级
        encoding = self.parent.download_options.encoding_input.text().strip()
        if encoding:
            command.extend(["-e", encoding])
            
        dfn = self.parent.download_options.dfn_input.text().strip()
        if dfn:
            command.extend(["-q", dfn])
            
        # 添加复选框选项
        if self.parent.download_options.use_aria2.isChecked():
            command.append("--use-aria2c")
        if self.parent.download_options.interactive.isChecked():
            command.append("-ia")
        if self.parent.download_options.download_danmaku.isChecked():
            command.append("-dd")
        if self.parent.download_options.video_only.isChecked():
            command.append("--video-only")
        if self.parent.download_options.audio_only.isChecked():
            command.append("--audio-only")
        if self.parent.download_options.skip_subtitle.isChecked():
            command.append("--skip-subtitle")
        if self.parent.download_options.skip_cover.isChecked():
            command.append("--skip-cover")
        if self.parent.download_options.debug.isChecked():
            command.append("--debug")
        if self.parent.download_options.show_all.isChecked():
            command.append("--show-all")
        if info_only:
            command.append("--only-show-info")
            
        # 添加文件命名模式
        file_pattern = self.parent.download_options.file_pattern.text().strip()
        if file_pattern:
            command.extend(["-F", file_pattern])
        else:
            command.extend(["-F", self.parent.default_file_pattern])
            
        multi_file_pattern = self.parent.download_options.multi_file_pattern.text().strip()
        if multi_file_pattern:
            command.extend(["-M", multi_file_pattern])
            
        # 添加工作目录
        work_dir = self.parent.download_options.work_dir.text().strip()
        if work_dir:
            command.extend(["--work-dir", work_dir])
            
        return command
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.parent.config_file):
            try:
                with open(self.parent.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                # 加载URL输入
                if 'url' in config:
                    self.parent.url_input.setText(config['url'])
                
                # 加载API模式
                if 'api_mode' in config:
                    index = self.parent.download_options.api_combo.findText(config['api_mode'])
                    if index >= 0:
                        self.parent.download_options.api_combo.setCurrentIndex(index)
                
                # 加载编码优先级
                if 'encoding' in config:
                    self.parent.download_options.encoding_input.setText(config['encoding'])
                
                # 加载画质优先级
                if 'dfn' in config:
                    self.parent.download_options.dfn_input.setText(config['dfn'])
                
                # 加载复选框状态
                if 'use_aria2' in config:
                    self.parent.download_options.use_aria2.setChecked(config['use_aria2'])
                if 'interactive' in config:
                    self.parent.download_options.interactive.setChecked(config['interactive'])
                if 'download_danmaku' in config:
                    self.parent.download_options.download_danmaku.setChecked(config['download_danmaku'])
                if 'video_only' in config:
                    self.parent.download_options.video_only.setChecked(config['video_only'])
                if 'audio_only' in config:
                    self.parent.download_options.audio_only.setChecked(config['audio_only'])
                if 'skip_subtitle' in config:
                    self.parent.download_options.skip_subtitle.setChecked(config['skip_subtitle'])
                if 'skip_cover' in config:
                    self.parent.download_options.skip_cover.setChecked(config['skip_cover'])
                if 'debug' in config:
                    self.parent.download_options.debug.setChecked(config['debug'])
                if 'show_all' in config:
                    self.parent.download_options.show_all.setChecked(config['show_all'])
                
                # 加载文件命名模式
                if 'file_pattern' in config:
                    self.parent.download_options.file_pattern.setText(config['file_pattern'])
                if 'multi_file_pattern' in config:
                    self.parent.download_options.multi_file_pattern.setText(config['multi_file_pattern'])
                
                # 加载工作目录
                if 'work_dir' in config:
                    self.parent.download_options.work_dir.setText(config['work_dir'])
                    
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            # 'url': self.parent.url_input.text(),
            'api_mode': self.parent.download_options.api_combo.currentText(),
            'encoding': self.parent.download_options.encoding_input.text(),
            'dfn': self.parent.download_options.dfn_input.text(),
            'use_aria2': self.parent.download_options.use_aria2.isChecked(),
            'interactive': self.parent.download_options.interactive.isChecked(),
            'download_danmaku': self.parent.download_options.download_danmaku.isChecked(),
            'video_only': self.parent.download_options.video_only.isChecked(),
            'audio_only': self.parent.download_options.audio_only.isChecked(),
            'skip_subtitle': self.parent.download_options.skip_subtitle.isChecked(),
            'skip_cover': self.parent.download_options.skip_cover.isChecked(),
            'debug': self.parent.download_options.debug.isChecked(),
            'show_all': self.parent.download_options.show_all.isChecked(),
            'file_pattern': self.parent.download_options.file_pattern.text(),
            'multi_file_pattern': self.parent.download_options.multi_file_pattern.text(),
            'work_dir': self.parent.download_options.work_dir.text()
        }
        
        try:
            with open(self.parent.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
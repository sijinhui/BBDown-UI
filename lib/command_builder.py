import shutil
from PySide6.QtWidgets import QMessageBox


class CommandBuilder:
    def __init__(self, parent):
        self.parent = parent
        self.BBDown_PATH = shutil.which("BBDown")

    def build_command(self, info_only=False):
        """构建BBDown命令"""
        url = self.parent.url_input.text().strip()
        if not url:
            QMessageBox.warning(self.parent, "警告", "请输入视频地址或BV号")
            return None
            
        # 转换新版个人空间合集链接为旧版格式
        converted_url = self.parent.url_handler.convert_space_url(url)

        command = [self.BBDown_PATH, converted_url]
        
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
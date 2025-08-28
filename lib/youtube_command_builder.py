import shutil
import subprocess
from PySide6.QtWidgets import QMessageBox


class YouTubeCommandBuilder:
    def __init__(self, parent):
        self.parent = parent
        self.YT_DLP_PATH = shutil.which("yt-dlp")
        if not self.YT_DLP_PATH:
            QMessageBox.warning(self.parent, "警告", "未找到yt-dlp程序，请确保已安装yt-dlp")

    def build_command(self, info_only=False):
        """构建yt-dlp命令"""
        url = self.parent.url_input.text().strip()
        if not url:
            QMessageBox.warning(self.parent, "警告", "请输入视频地址")
            return None
            
        if not self.YT_DLP_PATH:
            QMessageBox.warning(self.parent, "警告", "未找到yt-dlp程序，请确保已安装yt-dlp")
            return None
            
        command = [self.YT_DLP_PATH, url]
        
        # 添加格式参数
        format_choice = self.parent.youtube_options.format_combo.currentText()
        quality_choice = self.parent.youtube_options.quality_combo.currentText()
        
        # 构建格式字符串
        if format_choice != "默认":
            format_str = format_choice
            if quality_choice != "最佳":
                # 将画质选项转换为yt-dlp格式
                quality_map = {
                    "8K": "4320",
                    "4K": "2160",
                    "1080p": "1080",
                    "720p": "720",
                    "480p": "480",
                    "360p": "360"
                }
                if quality_choice in quality_map:
                    format_str += f"[height<={quality_map[quality_choice]}]"
            command.extend(["-f", format_str])
        
        # 添加音频格式参数
        audio_format = self.parent.youtube_options.audio_format_combo.currentText()
        if audio_format != "最佳":
            command.extend(["--extract-audio", "--audio-format", audio_format])
            
        # 添加选项参数
        if self.parent.youtube_options.subtitle_checkbox.isChecked():
            command.append("--write-sub")
        if self.parent.youtube_options.video_only.isChecked():
            command.append("--no-audio")
        if self.parent.youtube_options.audio_only.isChecked():
            command.extend(["--extract-audio", "--audio-format", "best"])
        if self.parent.youtube_options.debug.isChecked():
            command.append("--verbose")
        if self.parent.youtube_options.embed_subtitle.isChecked():
            command.append("--embed-subs")
        if self.parent.youtube_options.embed_thumbnail.isChecked():
            command.append("--embed-thumbnail")
        if self.parent.youtube_options.split_chapters.isChecked():
            command.append("--split-chapters")
        if info_only:
            command.append("--print-json")
            command.append("-F")
            
        # 添加文件命名模式
        file_pattern = self.parent.youtube_options.file_pattern.text().strip()
        if file_pattern:
            command.extend(["-o", file_pattern])
            
        # 添加工作目录
        work_dir = self.parent.youtube_options.work_dir.text().strip()
        if work_dir:
            command.extend(["--paths", work_dir])
            
        return command
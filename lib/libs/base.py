from PySide6.QtWidgets import QFileDialog
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from download_dir import downloads_path

class OptionsBase(object):
    def browse_directory(self):
        """浏览目录选择"""
        current_dir = self.work_dir.text().strip()
        if current_dir and Path(current_dir).exists() and Path(current_dir).is_dir():
            default_dir = current_dir
        else:
            default_dir = str(Path.home())

        directory = QFileDialog.getExistingDirectory(
            self.parent, "选择工作目录", default_dir
        )
        if directory:
            self.work_dir.setText(directory)

    def open_directory(self):
        """打开工作目录"""
        directory = self.work_dir.text().strip()
        p = Path(directory)
        if directory and p.exists() and p.is_dir():
            # 使用QDesktopServices打开目录
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
        else:
            # 如果目录不存在，尝试打开父目录或用户主目录
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(downloads_path)))
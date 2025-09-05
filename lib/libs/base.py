from PySide6.QtWidgets import QFileDialog
from pathlib import Path


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

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QLineEdit, QHBoxLayout


def check_bbdown_path(window):
    """检查BBDown路径是否存在"""
    if not window.command_builder.BBDown_PATH:
        # 创建弹窗
        dialog = QDialog(window)
        dialog.setWindowTitle("BBDown 未找到")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("未找到 BBDown 程序，请选择 BBDown 可执行文件：")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # 添加文本框
        path_input = QLineEdit()
        path_input.setPlaceholderText("请输入 BBDown 可执行文件路径")
        layout.addWidget(path_input)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        browse_button = QPushButton("选择文件")
        confirm_button = QPushButton("确认")
        cancel_button = QPushButton("取消")
        
        button_layout.addWidget(browse_button)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        def browse_file():
            file_path, _ = QFileDialog.getOpenFileName(window, "选择 BBDown 可执行文件")
            if file_path:
                path_input.setText(file_path)
                if os.path.exists(file_path):
                    window.command_builder.BBDown_PATH = file_path
                    window.download_options.BBDown_PATH = file_path
                    dialog.accept()
                else:
                    QMessageBox.warning(window, "错误", "所选文件不存在")
        
        def confirm_path():
            file_path = path_input.text().strip()
            if file_path:
                if os.path.exists(file_path):
                    window.command_builder.BBDown_PATH = file_path
                    window.download_options.BBDown_PATH = file_path
                    dialog.accept()
                else:
                    QMessageBox.warning(window, "错误", "所选文件不存在")
            else:
                QMessageBox.warning(window, "错误", "请输入有效的文件路径")
        
        def cancel_dialog():
            dialog.reject()
        
        browse_button.clicked.connect(browse_file)
        confirm_button.clicked.connect(confirm_path)
        cancel_button.clicked.connect(cancel_dialog)
        
        dialog.exec()
        
        # 如果用户取消了文件选择，退出程序
        if not window.command_builder.BBDown_PATH:
            sys.exit(1)


def setup_system_paths():
    """配置系统路径，方便在打包为app时获取类似ffmpeg等程序"""
    import platform

    # 检查操作系统类型
    system = platform.system()

    # 只在 macOS 和 Linux 上添加额外路径
    if system in ["Darwin", "Linux"]:
        # 添加常见的Unix-like系统二进制文件路径
        common_paths = [
            "~/.local/bin",
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
            "/usr/sbin",
            "/sbin"
        ]

        # 获取当前PATH环境变量
        current_path = os.environ.get("PATH", "")
        path_list = current_path.split(":") if current_path else []

        # 添加不在当前PATH中的常见路径
        for path in common_paths:
            p = str(Path(path).expanduser().resolve())
            if p not in path_list and os.path.exists(p):
                path_list.append(p)

        # 更新PATH环境变量
        os.environ["PATH"] = ":".join(path_list)
    # Windows系统不需要特殊处理，保持原有PATH即可


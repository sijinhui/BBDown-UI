from PySide6.QtWidgets import QHBoxLayout, QPushButton, QMessageBox
from .qr_dialog import QRCodeDialog
from PySide6.QtCore import QProcess



class ActionButtons:
    def __init__(self, parent):
        self.parent = parent
        self.download_button = None
        self.info_button = None
        self.login_button = None
        self.qr_dialog = None

    def create_action_buttons(self, layout):
        """创建执行按钮区域"""
        buttons_layout = QHBoxLayout()
        
        self.download_button = QPushButton("开始下载")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004477;
            }
        """)
        
        self.info_button = QPushButton("仅解析信息")
        self.info_button.clicked.connect(self.show_info)
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        self.login_button = QPushButton("登录账号")
        self.login_button.clicked.connect(self.login_account)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        
        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.info_button)
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
    def start_download(self):
        """开始下载"""
        command = self.parent.command_builder.build_command()
        if command:
            self.parent.output_area.clear_output()
            self.parent.output_area.append_output(f"执行命令: {' '.join(command)}")
            self.parent.process_handler.process.start(command[0], command[1:])
            self.download_button.setEnabled(False)
            
    def show_info(self):
        """仅显示信息"""
        command = self.parent.command_builder.build_command(info_only=True)
        if command:
            self.parent.output_area.clear_output()
            self.parent.output_area.append_output(f"执行命令: {' '.join(command)}")
            self.parent.process_handler.process.start(command[0], command[1:])
            self.info_button.setEnabled(False)
            
    def login_account(self):
        """登录账号"""
        self.parent.output_area.clear_output()
        self.parent.output_area.append_output("执行命令: BBDown login")
        self.parent.process_handler.start("BBDown", ["login"])
        self.login_button.setEnabled(False)
        
        # 显示二维码弹窗
        self.qr_dialog = QRCodeDialog(self.parent)
        self.qr_dialog.show()
        
    def process_finished(self):
        """进程结束处理"""
        self.download_button.setEnabled(True)
        self.info_button.setEnabled(True)
        self.login_button.setEnabled(True)
        self.parent.output_area.append_output("操作完成")
        
        # 关闭二维码弹窗（如果存在）
        if hasattr(self, 'qr_dialog') and self.qr_dialog:
            self.qr_dialog.close()
            self.qr_dialog = None
            
    def handle_not_logged_in(self):
        """处理未登录状态"""
        # 弹出提示框询问用户是否要登录
        reply = QMessageBox.question(self.parent, "未登录提示", 
                                   "检测到您尚未登录B站账号，解析可能受到限制。是否立即登录？", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # 中断当前进程
            if self.parent.process and self.parent.process_handler.state() == QProcess.ProcessState.Running:
                self.parent.process_handler.kill()
                self.parent.process_handler.waitForFinished()
            
            # 触发登录操作
            self.login_account()
        else:
            # 用户选择不登录，继续当前操作
            pass
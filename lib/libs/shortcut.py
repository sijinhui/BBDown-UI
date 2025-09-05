from PySide6.QtGui import QShortcut, QKeySequence


class ShortcutMixin:
    """快捷键混入类"""

    def setup_shortcuts(self):
        """设置快捷键 - 需要在窗口完全初始化后调用"""
        try:
            # Cmd+W 关闭窗口
            close_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
            close_shortcut.activated.connect(self.close)

            # 你可以在这里添加更多快捷键
            # refresh_shortcut = QShortcut(QKeySequence("F5"), self)
            # refresh_shortcut.activated.connect(self.refresh)

        except Exception as e:
            print(f"设置快捷键失败: {e}")
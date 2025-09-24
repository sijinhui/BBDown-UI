from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QLayout
)
from qfluentwidgets import ScrollArea

class BilibiliFav(ScrollArea):
    """收藏夹界面"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.setObjectName('favInterface')

    def create_fav_area(self, layout):
        fav_group = QGroupBox("收藏夹")
        fav_layout = QVBoxLayout(fav_group)

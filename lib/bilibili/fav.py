from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QLayout
)

class BilibiliFav:
    def __init__(self,):
        pass
    def create_fav_area(self, layout):
        fav_group = QGroupBox("收藏夹")
        fav_layout = QVBoxLayout(fav_group)

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QHeaderView, QFrame, QWidget)
from PySide6.QtCore import Qt, Slot
import qtawesome as qta
from components.framelessWindow import FramelessWindow
from components.table import CustomTable

class QueueWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("KGM Download Queue Base")
        self.resize(750, 450)
        self.setup_queue_body()

    def setup_queue_body(self):
        self.main_widget = QWidget(self.content_area)
        self.main_widget.setObjectName("queueWindowBody")
        
        container = QVBoxLayout(self.content_area)
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(0)
        container.addWidget(self.main_widget)
        
        widget_layout = QVBoxLayout(self.main_widget)
        widget_layout.setContentsMargins(20, 20, 20, 20)
        widget_layout.setSpacing(15)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.queue_input = QLineEdit()
        self.queue_input.setPlaceholderText("Queue up next video or playlist URL...")
        self.queue_input.setObjectName("urlInput")
        self.queue_input.setMinimumHeight(38)

        self.append_queue_btn = QPushButton(" Queue Link")
        self.append_queue_btn.setObjectName("fetchUrlBtn")
        self.append_queue_btn.setMinimumHeight(38)
        self.append_queue_btn.setFixedWidth(120)
        
        input_layout.addWidget(self.queue_input)
        input_layout.addWidget(self.append_queue_btn)
        widget_layout.addLayout(input_layout)

        self.queue_table = CustomTable(0, 3)
        self.queue_table.setObjectName("customTable")
        self.queue_table.setHorizontalHeaderLabels(["Index", "Target URL Source Link", "Status State"])
        self.queue_table.setColumnWidth(0, 50)
        self.queue_table.setColumnWidth(2, 120)
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        widget_layout.addWidget(self.queue_table)

        self.update_queue_theme_icons("#ffffff")

    def update_icon(self, is_light):
        icon_color = "#222222" if is_light else "#ffffff"
        icon_name = 'fa5s.sun' if is_light else 'fa5s.moon'
        pixmap = qta.icon(icon_name, color=icon_color).pixmap(18, 18)
        self.theme_icon.setPixmap(pixmap)
        
    def update_queue_theme_icons(self, color):
        self.append_queue_btn.setIcon(qta.icon('fa5s.plus', color=color))
        
        if hasattr(self, 'title_bar'):
            if hasattr(self.title_bar, 'title_label'):
                self.title_bar.title_label.style().unpolish(self.title_bar.title_label)
                self.title_bar.title_label.style().polish(self.title_bar.title_label)
            
            self.title_bar.style().unpolish(self.title_bar)
            self.title_bar.style().polish(self.title_bar)
            
            control_icons = {
                'minBtn': 'fa5s.window-minimize',
                'maxBtn': 'fa5s.window-maximize',
                'closeBtn': 'fa5s.times'
            }
            
            for attr_name, icon_string in control_icons.items():
                btn = getattr(self.title_bar, attr_name, None)
                if btn:
                    btn.setIcon(qta.icon(icon_string, color=color))
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
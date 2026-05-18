from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QProgressBar, QFrame, QApplication)
from PySide6.QtCore import Qt
import qtawesome as qta
from components.table import CustomTable

class MainContentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # 1. Add URL Button (The dashed zone)
        self.add_url_btn = QPushButton("+ Add URL")
        self.add_url_btn.setObjectName("addUrlBtn")
        self.add_url_btn.setMinimumHeight(100)
        self.layout.addWidget(self.add_url_btn)

        # 2. Reusable Table
        self.table = CustomTable(0, 8)
        self.table.setHorizontalHeaderLabels([
            "", "FileName", "ProgressStatus", "FileSize", "CurrentStatus", "DownloadSpeed", "TimeLeft", "DateAdded"
        ])
        # Fix the first column width for checkboxes/icons
        self.table.setColumnWidth(0, 40)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        
        self.layout.addWidget(self.table)

        # 3. Info Panel
        self.info_panel = QFrame()
        self.info_panel.setObjectName("infoPanel")
        self.info_panel.setFixedHeight(130)
        # (Inside setup_info_panel logic would go here)
        self.layout.addWidget(self.info_panel)

    def setup_info_panel(self):
        layout = QHBoxLayout(self.info_panel)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Initial icon state - using the white/dark logic from your TitleBar
        # We start with white (Dark Mode default)
        self.folder_icon_label.setPixmap(qta.icon('fa5s.folder', color='#ffffff').pixmap(70, 70))
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        
        self.detail_name = QLabel("Name: Queen of Katwe.mp4")
        self.detail_name.setObjectName("detailName")
        
        self.detail_progress = QProgressBar()
        self.detail_progress.setValue(65)
        self.detail_progress.setFixedHeight(12)
        self.detail_progress.setTextVisible(False)
        self.detail_progress.setObjectName("detailProgressBar")
        
        self.detail_path = QLabel("Path: C://Users/Desktop/Newfolder")
        self.detail_path.setObjectName("detailPath")
        
        details_layout.addStretch()
        details_layout.addWidget(self.detail_name)
        details_layout.addWidget(self.detail_progress)
        details_layout.addWidget(self.detail_path)
        details_layout.addStretch()
        
        layout.addWidget(self.folder_icon_label)
        layout.addLayout(details_layout)
        layout.addStretch()

    def update_theme_icons(self, color):
        """
        This is the heart of your theming system. 
        It's called by CustomTitleBar.switch_theme to flip colors.
        """
        # Update the big folder icon
        self.folder_icon_label.setPixmap(
            qta.icon('fa5s.folder', color=color).pixmap(70, 70)
        )
        
        # Refresh the palette to ensure QSS rules (like text color) apply immediately
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
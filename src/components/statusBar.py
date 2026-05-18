from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
import qtawesome as qta

class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)
        self.setObjectName("statusBar")
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        self.status_label = QLabel("Status: Idle!")
        
        self.update_btn = QPushButton(" Check for Updates")
        self.update_btn.setObjectName("statusBarUpdateBtn")
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setFixedHeight(25)
        
        self.layout.addWidget(self.status_label)
        self.layout.addStretch()
        self.layout.addWidget(self.update_btn)
        
        self.update_theme_icons("#ffffff")

    def update_theme_icons(self, color):
        self.update_btn.setIcon(qta.icon('fa5s.sync-alt', color=color))
        
        self.style().unpolish(self)
        self.style().polish(self)
        
        for label in self.findChildren(QLabel):
            label.style().unpolish(label)
            label.style().polish(label)
            
        self.update_btn.style().unpolish(self.update_btn)
        self.update_btn.style().polish(self.update_btn)
            
        self.update()
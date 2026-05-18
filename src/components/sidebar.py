from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation
import qtawesome as qta

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(40)
        
        # This tells the frame to paint its background using the QSS
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 20, 0, 20)
        
        self.layout.addStretch()
        
        self.settings_icon = QLabel()
        self.settings_icon.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.settings_icon)
        
        # Initial call
        self.update_theme_icons("#ffffff")

    def update_theme_icons(self, color):
        # 1. Update the Gear icon color
        self.settings_icon.setPixmap(qta.icon('fa5s.cog', color=color).pixmap(25, 25))
        
        # 2. Force the CSS refresh
        # We re-apply the style to ensures the {{secondary_bg}} 
        # from your new stylesheet is actually painted.
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
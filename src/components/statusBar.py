from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
import qtawesome as qta

class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)
        self.setObjectName("statusBar")
        
        # Ensures the QFrame follows the background-color and border from QSS
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        self.status_label = QLabel("Status: Idle!")
        
        # Speed Indicators Container
        self.speed_widget = QWidget()
        speed_layout = QHBoxLayout(self.speed_widget)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        
        self.up_icon = QLabel()
        self.up_val = QLabel("Upload: 1.3 Mps")
        
        self.sep = QLabel("|")
        # Removed hardcoded inline style to make it theme-responsive
        
        self.down_icon = QLabel()
        self.down_val = QLabel("Download: 1.3 Mps")

        speed_layout.addWidget(self.up_icon)
        speed_layout.addWidget(self.up_val)
        speed_layout.addWidget(self.sep)
        speed_layout.addWidget(self.down_icon)
        speed_layout.addWidget(self.down_val)
        
        self.layout.addWidget(self.status_label)
        self.layout.addStretch()
        self.layout.addWidget(self.speed_widget)
        
        # Initial call (Default to Dark Mode color)
        self.update_theme_icons("#ffffff")

    def update_theme_icons(self, color):
        """
        Updates icon colors and forces a style refresh for text and borders.
        """
        # 1. Update Icons
        self.up_icon.setPixmap(qta.icon('fa5s.caret-up', color='#00d4ff').pixmap(12, 12))
        self.down_icon.setPixmap(qta.icon('fa5s.caret-down', color='#00ffcc').pixmap(12, 12))
        
        # 2. Update the separator color dynamically if not handled by QSS
        sep_color = "#444444" if color == "#ffffff" else "#cccccc"
        self.sep.setStyleSheet(f"color: {sep_color};")
        
        # 3. Force Style Refresh
        # This makes the status bar re-read 'border-top' and 'color' from your QSS variables
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Explicitly polish children to ensure text color (text_main) updates
        for label in self.findChildren(QLabel):
            label.style().unpolish(label)
            label.style().polish(label)
            
        self.update()
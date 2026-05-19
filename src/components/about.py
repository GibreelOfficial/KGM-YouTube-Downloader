import os
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices
from components.framelessWindow import FramelessWindow
import qtawesome as qta

from utils.paths import ASSETS_DIR

class AboutDialog(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__()
        
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("About KGM Downloader")
        self.resize(380, 440)
        
        self.title_bar.theme_toggle.setVisible(False)
        self.title_bar.btn_min.setVisible(False)
        self.title_bar.btn_max.setVisible(False)
        
        body_layout = QVBoxLayout(self.content_area)
        body_layout.setContentsMargins(30, 25, 30, 25)
        body_layout.setSpacing(14)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(QSize(75, 75), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        
        body_layout.addWidget(self.logo_label)

        self.title = QLabel("KGM YouTube Downloader")
        self.title.setObjectName("aboutTitle")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.version = QLabel("Version 2.0.0 beta_1")
        self.version.setObjectName("aboutCredits")
        self.version.setAlignment(Qt.AlignCenter)
        
        self.credits_lbl = QLabel("Developed by Kisakye Gibreel\n© May 2026 KGM. All rights reserved.")
        self.credits_lbl.setObjectName("aboutCredits")
        self.credits_lbl.setAlignment(Qt.AlignCenter)

        self.support_container = QWidget()
        self.support_container.setObjectName("supportContainer")
        support_layout = QVBoxLayout(self.support_container)
        support_layout.setSpacing(10)
        support_layout.setContentsMargins(12, 10, 12, 10)

        support_title = QLabel("Support the Developer")
        support_title.setObjectName("supportTitle")
        support_title.setAlignment(Qt.AlignCenter)

        self.kofi_btn = QPushButton(" Support on Ko-fi")
        self.kofi_btn.setObjectName("kofiSupportBtn")
        self.kofi_btn.setFixedHeight(34)
        self.kofi_btn.setCursor(Qt.PointingHandCursor)
        self.kofi_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/gibreeltheone")))

        momo_layout = QHBoxLayout()
        momo_layout.setSpacing(6)
        momo_layout.setAlignment(Qt.AlignCenter)
        
        self.momo_icon = QLabel()
        self.momo_lbl = QLabel("Mobile Money (Airtel): 0708996763")
        self.momo_lbl.setObjectName("momoLabel")
        
        momo_layout.addWidget(self.momo_icon)
        momo_layout.addWidget(self.momo_lbl)

        support_layout.addWidget(support_title)
        support_layout.addWidget(self.kofi_btn)
        support_layout.addLayout(momo_layout)
        
        btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("aboutCloseBtn")
        self.close_btn.setFixedWidth(110)
        self.close_btn.setFixedHeight(34)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        
        body_layout.addWidget(self.title)
        body_layout.addWidget(self.version)
        body_layout.addWidget(self.credits_lbl)
        body_layout.addSpacing(4)
        body_layout.addWidget(self.support_container)
        body_layout.addSpacing(4)
        body_layout.addLayout(btn_layout)

        if parent and hasattr(parent, 'current_theme_color'):
            self.update_theme_icons(parent.current_theme_color)
        else:
            self.update_theme_icons("#9ec100")

    def update_theme_icons(self, color):
        self.kofi_btn.setIcon(qta.icon('fa5s.coffee', color=color))
        self.momo_icon.setPixmap(qta.icon('fa5s.mobile-alt', color=color).pixmap(14, 14))
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.title_bar.style().unpolish(self.title_bar)
        self.title_bar.style().polish(self.title_bar)
        self.update()
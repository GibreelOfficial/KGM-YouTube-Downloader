import sys
import os
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from utils.paths import ASSETS_DIR
from utils.theme_loader import load_stylesheet
from components.buttons import ThemeToggle
import qtawesome as qta

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("CustomTitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        self.layout.setSpacing(10)
        
        self.theme_icon = QLabel()
        self.theme_icon.setFixedSize(18, 18)
        self.theme_icon.setObjectName("themeIcon")
        
        self.theme_toggle = ThemeToggle()
        self.theme_toggle.toggled.connect(self.switch_theme)
        
        self.update_icon(False) 

        self.app_logo = QLabel()
        self.app_logo.setObjectName("appLogo")
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo_pixmap = QPixmap(os.path.abspath(logo_path))
        self.app_logo.setPixmap(logo_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.app_logo.setFixedSize(20, 20)
        
        self.title_text = QLabel("KGM YouTube Downloader")
        self.title_text.setObjectName("titleLabel")
        
        icon_color = "#ffffff"
        
        self.btn_min = QPushButton()
        self.btn_min.setIcon(qta.icon('fa5s.minus', color=icon_color))
        self.btn_max = QPushButton()
        self.btn_max.setIcon(qta.icon('fa5s.square', color=icon_color))
        self.btn_close = QPushButton()
        self.btn_close.setIcon(qta.icon('fa5s.times', color=icon_color))
        
        self.btn_min.setObjectName("minBtn")
        self.btn_max.setObjectName("maxBtn")
        self.btn_close.setObjectName("closeBtn")

        self.setup_platform_ui()
        
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self.handle_maximize)
        self.btn_close.clicked.connect(self.parent.close)

    def setup_platform_ui(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget(): item.widget().hide()

        theme_controls = [self.theme_icon, self.theme_toggle]

        if sys.platform == "darwin": 
            self.layout.addWidget(self.btn_close)
            self.layout.addWidget(self.btn_min)
            self.layout.addWidget(self.btn_max)
            self.layout.addStretch()
            for widget in theme_controls: self.layout.addWidget(widget)
            self.layout.addSpacing(10)
            self.layout.addWidget(self.title_text)
            self.layout.addWidget(self.app_logo)
        else: 
            self.layout.addWidget(self.app_logo)
            self.layout.addWidget(self.title_text)
            self.layout.addStretch()
            for widget in theme_controls: self.layout.addWidget(widget)
            self.layout.addSpacing(10)
            self.layout.addWidget(self.btn_min)
            self.layout.addWidget(self.btn_max)
            self.layout.addWidget(self.btn_close)

    def update_icon(self, is_light):
        icon_color = "#222222" if is_light else "#ffffff"
        icon_name = 'fa5s.sun' if is_light else 'fa5s.moon'
        pixmap = qta.icon(icon_name, color=icon_color).pixmap(18, 18)
        self.theme_icon.setPixmap(pixmap)

    def set_title_bar_color(self, hex_color):
        self.btn_min.setIcon(qta.icon('fa5s.minus', color=hex_color))
        self.btn_max.setIcon(qta.icon('fa5s.square', color=hex_color))
        self.btn_close.setIcon(qta.icon('fa5s.times', color=hex_color))
        self.title_text.setStyleSheet(f"color: {hex_color};")
        
        is_light = hex_color == "#222222"
        self.update_icon(is_light)
        
        for element in [self.title_text, self.btn_min, self.btn_max, self.btn_close]:
            element.style().unpolish(element)
            element.style().polish(element)

    def switch_theme(self, checked):
        theme_name = "light_neon" if checked else "dark_neon"
        try:
            new_style = load_stylesheet(theme_name)
            QApplication.instance().setStyleSheet(new_style)
            
            dynamic_color = "#222222" if checked else "#ffffff"
            self.set_title_bar_color(dynamic_color)
            self.theme_toggle.set_theme_colors(dynamic_color)
            
            if hasattr(self.parent, 'main_content'):
                self.parent.main_content.update_theme_icons(dynamic_color)
            
            if hasattr(self.parent, 'sidebar_settings_icon'):
                self.parent.sidebar_settings_icon.setPixmap(
                    qta.icon('fa5s.cog', color=dynamic_color).pixmap(25, 25)
                )
            
        except Exception as e:
            print(f"Theme Error: {e}")

    def handle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if self.childAt(event.position().toPoint()):
            return
        if event.button() == Qt.LeftButton:
            self.initial_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.initial_pos)
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.initial_pos = event.globalPosition().toPoint()

class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setObjectName("windowContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.content_area = QWidget() 
        self.content_area.setObjectName("contentArea")
        
        self.container_layout.addWidget(self.title_bar)
        self.container_layout.addWidget(self.content_area, 1)
        
        self.main_layout.addWidget(self.container)

    def update_theme_icons(self, color):
        if hasattr(self, 'title_bar'):
            self.title_bar.set_title_bar_color(color)
            self.title_bar.style().unpolish(self.title_bar)
            self.title_bar.style().polish(self.title_bar)
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
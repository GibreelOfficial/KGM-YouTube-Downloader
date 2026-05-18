from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor

class ThemeToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 22)
        self.setCursor(Qt.PointingHandCursor)
        
        self._bg_color = QColor("#ffffff") 
        self._knob_color = QColor("#ffffff")
        self._knob_position = 3
        
        self.animation = QPropertyAnimation(self, b"knob_position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    @Property(int)
    def knob_position(self):
        return self._knob_position

    @knob_position.setter
    def knob_position(self, pos):
        self._knob_position = pos
        self.update()

    # This is more reliable than checkStateSet for mouse clicks
    def nextCheckState(self):
        super().nextCheckState()
        state = self.isChecked()
        self.start_transition(state)

    def start_transition(self, checked):
        self.animation.stop()
        self.animation.setEndValue(23 if checked else 3)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Pill Outline
        p.setPen(self._bg_color)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 10, 10)

        # Knob
        p.setPen(Qt.NoPen)
        p.setBrush(self._knob_color)
        p.drawEllipse(self._knob_position, 3, 16, 16)

    def set_theme_colors(self, color_hex):
        self._bg_color = QColor(color_hex)
        self._knob_color = QColor(color_hex)
        self.update()
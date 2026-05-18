from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QStyledItemDelegate
from PySide6.QtCore import Qt, QSize

class TableDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width(), 40) # Slightly tighter row height

class CustomTable(QTableWidget):
    def __init__(self, rows=0, cols=8, parent=None):
        super().__init__(rows, cols, parent)
        self.setObjectName("customTable")
        self.setItemDelegate(TableDelegate(self))
        self.setup_ui()

    def setup_ui(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setHighlightSections(False)
        
        # Reduced header height for a sleeker look
        header.setMinimumHeight(30) 
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFrameShape(QTableWidget.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def update_theme_icons(self, color):
        self.style().unpolish(self)
        self.style().polish(self)
        header = self.horizontalHeader()
        header.style().unpolish(header)
        header.style().polish(header)
        self.viewport().update() 
        self.update()
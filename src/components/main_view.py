import os
import json
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QHeaderView, QProgressBar, QFrame, QTableWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
import qtawesome as qta
from components.table import CustomTable

class MainContentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainContentView")
        
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "downloads_history.json"))
        self.current_theme_color = "#ffffff"
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(35, 30, 35, 30)
        self.layout.setSpacing(25)

        self.setup_top_control_panel()

        self.table = CustomTable(0, 8)
        self.table.setObjectName("customTable")
        
        self.table.setHorizontalHeaderLabels([
            "", "Name", "Progress", "Size", "Status", "Speed", "Time left", "Date Added"
        ])
        trash_icon = qta.icon('fa5s.trash-alt', color='#e51c23')
        self.table.horizontalHeaderItem(0).setIcon(trash_icon)
        
        self.table.setShowGrid(False)
        self.table.setColumnWidth(0, 45)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.info_panel = QFrame()
        self.info_panel.setObjectName("infoPanel")
        self.info_panel.setFixedHeight(90)
        
        self.folder_icon_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        
        self.setup_info_panel()
        self.layout.addWidget(self.info_panel)
        
        self.load_history_from_json()

    def update_active_progress(self, percent_value, status_text=None):
        self.progress_bar.setValue(int(percent_value))
        
        speed = "---"
        eta = "---"
        
        if status_text:
            if status_text.startswith("PROGRESS_DATA|"):
                try:
                    _, speed, eta = status_text.split("|")
                    self.detail_name.setText(f"Downloading... Speed: {speed} | Time Left: {eta}")
                except Exception:
                    pass
            else:
                self.detail_name.setText(status_text)
                
        if self.table.rowCount() > 0:
            active_row = self.table.rowCount() - 1
            
            row_widget = self.table.cellWidget(active_row, 2)
            if isinstance(row_widget, QProgressBar):
                row_widget.setValue(int(percent_value))
                if percent_value > 0 and row_widget.property("statusClass") != "queued":
                    row_widget.setProperty("statusClass", "queued")
                    row_widget.style().unpolish(row_widget)
                    row_widget.style().polish(row_widget)
                
            if speed != "---":
                self.create_themed_table_item(active_row, 5, speed)
            if eta != "---":
                self.create_themed_table_item(active_row, 6, eta)

    def handle_download_finished(self, final_state_string):
        is_done = final_state_string == "complete"
        self.progress_bar.setValue(100 if is_done else 0)
        self.detail_name.setText(f"Status: Download {final_state_string}")
        
        css_class = "complete" if is_done else "failed"
        self.progress_bar.setProperty("statusClass", css_class)
        self.progress_bar.style().unpolish(self.progress_bar)
        self.progress_bar.style().polish(self.progress_bar)
        
        if self.table.rowCount() > 0:
            active_row = self.table.rowCount() - 1
            
            row_progress = self.table.cellWidget(active_row, 2)
            if isinstance(row_progress, QProgressBar):
                row_progress.setValue(100 if is_done else 0)
                row_progress.setProperty("statusClass", css_class)
                row_progress.style().unpolish(row_progress)
                row_progress.style().polish(row_progress)
                
            self.update_row_status(active_row, final_state_string)
            self.create_themed_table_item(active_row, 5, "---")
            self.create_themed_table_item(active_row, 6, "---")

    def set_progress_status_style(self, status_class):
        if self.progress_bar.property("statusClass") != status_class:
            self.progress_bar.setProperty("statusClass", status_class)
            self.progress_bar.style().unpolish(self.progress_bar)
            self.progress_bar.style().polish(self.progress_bar)
            self.progress_bar.update()
            
    def setup_top_control_panel(self):
        control_frame = QFrame()
        control_frame.setObjectName("topControlPanel")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(15)

        url_layout = QHBoxLayout()
        url_layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube link here...")
        self.url_input.setObjectName("urlInput")
        self.url_input.setMinimumHeight(45)

        self.add_url_btn = QPushButton(" Download")
        self.add_url_btn.setObjectName("fetchUrlBtn")
        self.add_url_btn.setMinimumHeight(45)
        self.add_url_btn.setFixedWidth(135)

        self.queue_window_btn = QPushButton()
        self.queue_window_btn.setObjectName("queueWindowBtn")
        self.queue_window_btn.setMinimumHeight(45)
        self.queue_window_btn.setFixedWidth(45)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_url_btn)
        url_layout.addWidget(self.queue_window_btn)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)

        self.dest_label = QLabel("Save to:")
        self.dest_label.setObjectName("destLabel")
        
        self.detail_path = QLabel("")
        self.detail_path.setObjectName("detailPathDisplay")

        self.browse_btn = QPushButton(" Browse...")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setFixedHeight(32)

        path_layout.addWidget(self.dest_label)
        path_layout.addWidget(self.detail_path, 1)
        path_layout.addWidget(self.browse_btn)

        control_layout.addLayout(url_layout)
        control_layout.addLayout(path_layout)
        self.layout.addWidget(control_frame)

    def setup_info_panel(self):
        layout = QHBoxLayout(self.info_panel)
        layout.setContentsMargins(25, 10, 25, 10)
        self.folder_icon_label.setAlignment(Qt.AlignCenter)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        
        self.detail_name = QLabel("No active download running")
        self.detail_name.setObjectName("detailName")
        
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setProperty("statusClass", "queued")
        
        details_layout.addStretch()
        details_layout.addWidget(self.detail_name)
        details_layout.addWidget(self.progress_bar)
        details_layout.addStretch()
        
        layout.addWidget(self.folder_icon_label)
        layout.addLayout(details_layout, 1)
        
        self.update_theme_icons(self.current_theme_color)

    def load_history_from_json(self):
        self.table.setRowCount(0)
        if not os.path.exists(self.db_path):
            return
            
        try:
            with open(self.db_path, "r") as f:
                history_data = json.load(f)
                
            for record in history_data:
                self.add_record_to_table_ui(record)
        except Exception:
            pass

    def create_themed_table_item(self, row, column, text):
        item = QTableWidgetItem(text)
        item.setForeground(QBrush(QColor(self.current_theme_color)))
        self.table.setItem(row, column, item)

    def add_record_to_table_ui(self, record):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        delete_btn = QPushButton()
        delete_btn.setFixedSize(28, 28)
        delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#e51c23'))
        delete_btn.setStyleSheet("background: transparent; border: none; padding: 0;")
        delete_btn.setCursor(Qt.PointingHandCursor)
        
        tracking_item = QTableWidgetItem()
        self.table.setItem(row, 0, tracking_item)
        delete_btn.clicked.connect(lambda checked=False, item=tracking_item: self.delete_record_by_item_trigger(item))
        
        container = QWidget()
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(delete_btn)
        self.table.setCellWidget(row, 0, container)
        
        title = record.get("title", "Unknown Download")
        size = record.get("size", "N/A")
        status = record.get("status", "complete")
        date_str = record.get("date", "")
        
        self.create_themed_table_item(row, 1, title)
        
        row_progress = QProgressBar()
        row_progress.setFixedHeight(8)
        row_progress.setTextVisible(False)
        
        status_clean = status.lower().strip()
        if status_clean in ["complete", "done"]:
            row_progress.setValue(100)
            row_progress.setProperty("statusClass", "complete")
        elif status_clean == "failed":
            row_progress.setValue(0)
            row_progress.setProperty("statusClass", "failed")
        else:
            row_progress.setValue(0)
            row_progress.setProperty("statusClass", "queued")
            
        self.table.setCellWidget(row, 2, row_progress)
        self.create_themed_table_item(row, 3, size)
        
        self.update_row_status(row, status)
        
        self.create_themed_table_item(row, 5, "---")
        self.create_themed_table_item(row, 6, "---")
        self.create_themed_table_item(row, 7, date_str)

    def handle_download_started(self, title, size, date_str):
        self.detail_name.setText(f"Downloading: {title}")
        self.progress_bar.setValue(0)
        self.progress_bar.setProperty("statusClass", "queued")
        self.progress_bar.style().unpolish(self.progress_bar)
        self.progress_bar.style().polish(self.progress_bar)
        
        mock_record = {
            "title": title,
            "size": size,
            "status": "downloading",
            "date": date_str
        }
        self.add_record_to_table_ui(mock_record)

    def delete_record_by_item_trigger(self, item):
        row_index = self.table.row(item)
        if row_index == -1:
            return
            
        try:
            with open(self.db_path, "r") as f:
                history_data = json.load(f)
        except Exception:
            return

        if row_index < len(history_data):
            history_data.pop(row_index)
            
        try:
            with open(self.db_path, "w") as f:
                json.dump(history_data, f, indent=4)
        except Exception:
            pass
            
        self.load_history_from_json()

    def update_row_status(self, row_index, state_string):
        state = state_string.lower().strip()
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignCenter)
        
        if state in ["complete", "done"]:
            status_label.setText("complete")
            status_label.setStyleSheet("""
                color: #8bc34a; border: 1px solid #8bc34a; border-radius: 10px; padding: 2px 8px; background: transparent; font-size: 11px;
            """)
        elif state in ["queued", "quede"]:
            status_label.setText("queued")
            status_label.setStyleSheet("""
                color: #03a9f4; border: 1px solid #03a9f4; border-radius: 10px; padding: 2px 8px; background: transparent; font-size: 11px;
            """)
        elif state == "failed":
            status_label.setText("failed")
            status_label.setStyleSheet("""
                color: #e51c23; border: 1px solid #e51c23; border-radius: 10px; padding: 2px 8px; background: transparent; font-size: 11px;
            """)
        elif state in ["downloading", "active"]:
            status_label.setText("active")
            status_label.setStyleSheet("""
                color: #ff9800; border: 1px solid #ff9800; border-radius: 10px; padding: 2px 8px; background: transparent; font-size: 11px;
            """)
            
        self.table.setCellWidget(row_index, 4, status_label)
   
    def update_theme_icons(self, color):
        self.current_theme_color = color
        
        self.folder_icon_label.setPixmap(qta.icon('fa5s.download', color=color).pixmap(24, 24))
        self.add_url_btn.setIcon(qta.icon('fa5s.arrow-alt-circle-down', color=color))
        self.browse_btn.setIcon(qta.icon('fa5s.folder-open', color=color))
        self.queue_window_btn.setIcon(qta.icon('fa5s.list-ol', color=color))
        
        for row in range(self.table.rowCount()):
            for col in [1, 3, 5, 6, 7]:
                item = self.table.item(row, col)
                if item:
                    item.setForeground(QBrush(QColor(color)))
                    
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class DeletedFileView(QWidget):
    def __init__(self, username, roles, primary_role, token, stack=None):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token

        self.stack: QStackedWidget = stack
        self.setWindowTitle("Deleted Files")
        main_layout = QVBoxLayout()

        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")

        search_bar = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search Deleted Files...")
        search_bar.setMinimumWidth(200)

        back_btn.clicked.connect(self.go_back)
        header = QLabel("Deleted Files")
        header.setFont(QFont("Arial", 16))
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        header_layout.addWidget(back_btn)
        main_layout.addLayout(header_layout)

        # Table logic (same as CollectionView)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Filename", "Time", "Extension", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.handle_item_clicked)

        # Sample data for demonstration - 10 files
        files_data = [
            ("Deleted File 1", "10:00 am", "pdf"),
            ("Deleted File 2", "11:30 am", "docx"),
            ("Deleted File 3", "2:15 pm", "xlsx"),
            ("Deleted File 4", "3:45 pm", "pdf"),
            ("Deleted File 5", "5:00 pm", "txt"),
            ("Deleted File 6", "6:20 pm", "jpg"),
            ("Deleted File 7", "7:10 pm", "pptx"),
            ("Deleted File 8", "8:30 pm", "zip"),
            ("Deleted File 9", "9:45 pm", "csv"),
            ("Deleted File 10", "10:55 pm", "mp4"),
        ]
        for name, time, ext in files_data:
            self.add_file_to_table(name, time, ext)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def create_actions_widget(self, filename):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        details_btn = QPushButton("Details")
        erase_btn = QPushButton("Erase")
        restore_btn = QPushButton("Restore")
        details_btn.clicked.connect(lambda: print(f"Details clicked for {filename}"))
        erase_btn.clicked.connect(lambda: print(f"Erase clicked for {filename}"))
        restore_btn.clicked.connect(lambda: print(f"Restore clicked for {filename}"))
        layout.addWidget(details_btn)
        layout.addWidget(erase_btn)
        layout.addWidget(restore_btn)
        widget.setLayout(layout)
        return widget

    def go_back(self):
        print("Back button clicked")
        if self.stack:
            self.stack.setCurrentIndex(0)  # Assuming dashboard is at index 0

    def add_file_to_table(self, name, time, ext):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(time))
        self.table.setItem(row, 2, QTableWidgetItem(ext))
        actions_widget = self.create_actions_widget(name)
        self.table.setCellWidget(row, 3, actions_widget)

    def handle_item_clicked(self, item):
        if item.column() != 3:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            print(f"Deleted file row clicked: {filename}")

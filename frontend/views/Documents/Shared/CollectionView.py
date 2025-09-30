from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class CollectionView(QWidget):
    def __init__(self, username, roles, primary_role, token, collection_name=None, stack=None):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token

        self.stack: QStackedWidget = stack
        self.setWindowTitle(f"Collection: {collection_name}" if collection_name else "Collection")
        main_layout = QVBoxLayout()

        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")

        search_bar = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search Organization...")
        search_bar.setMinimumWidth(200)

        back_btn.clicked.connect(self.go_back)
        header = QLabel(f"{collection_name}" if collection_name else "Collection")
        header.setFont(QFont("Arial", 16))
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        header_layout.addWidget(back_btn)
        main_layout.addLayout(header_layout)

        # Table logic (same as AdminDash)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Filename", "Time", "Extension", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.handle_item_clicked)  # Added this

        # Sample data for demonstration
        files_data = [
            (f"{collection_name} File 1", "10:00 am", "pdf"),
            (f"{collection_name} File 2", "11:30 am", "docx"),
            (f"{collection_name} File 3", "2:15 pm", "xlsx"),
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
        reject_btn = QPushButton("Reject")
        accept_btn = QPushButton("Accept")
        details_btn.clicked.connect(lambda: print(f"Details clicked for {filename}"))
        reject_btn.clicked.connect(lambda: print(f"Reject clicked for {filename}"))
        accept_btn.clicked.connect(lambda: print(f"Accept clicked for {filename}"))
        layout.addWidget(details_btn)
        layout.addWidget(reject_btn)
        layout.addWidget(accept_btn)
        widget.setLayout(layout)
        return widget

    def go_back(self):
        print("Back button clicked")  # Added this
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

    def handle_item_clicked(self, item):  # Renamed and updated
        if item.column() != 3:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            print(f"File row clicked: {filename}")
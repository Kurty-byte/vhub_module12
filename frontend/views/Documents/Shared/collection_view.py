from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal
from ..controller.document_controller import DocumentController
from ..Mock.data_loader import get_collection_by_name

class CollectionView(QWidget):
    file_accepted = pyqtSignal(str)
    file_rejected = pyqtSignal(str)

    file_uploaded = pyqtSignal(dict)

    def __init__(self, username, roles, primary_role, token, collection_name=None, stack=None):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.collection_name = collection_name
        
        # Initialize controller
        self.controller = DocumentController(username, roles, primary_role, token)

        self.stack: QStackedWidget = stack
        self.setWindowTitle(f"Collection: {collection_name}" if collection_name else "Collection")
        main_layout = QVBoxLayout()

        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.go_back)
        
        header = QLabel(f"{collection_name}" if collection_name else "Collection")
        header.setFont(QFont("Arial", 16))
        
        # Add File button
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.handle_add_file)

        search_bar = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search files...")
        search_bar.setMinimumWidth(200)

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(add_file_btn)
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

        # Load collection data from JSON
        collection_data = get_collection_by_name(collection_name)
        if collection_data:
            files_data = collection_data.get('files', [])
            for file_data in files_data:
                self.add_file_to_table(file_data['filename'], file_data['time'], file_data['extension'])
        else:
            # Fallback if collection not found
            print(f"Warning: Collection '{collection_name}' not found in JSON data")
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
    
    def handle_add_file(self):
        """Open file upload dialog for this collection"""
        print(f"Add file to collection: {self.collection_name}")
        from ..services.document_crud_service import DocumentCRUDService
        from .file_upload_dialog import FileUploadDialog
        
        # Get collection ID
        crud_service = DocumentCRUDService()
        collection = crud_service.get_collection_by_name(self.collection_name)
        
        if collection:
            collection_id = collection.get("id")
            dialog = FileUploadDialog(
                self, 
                collection_id=collection_id,
                username=self.username,
                role=self.primary_role
            )
            dialog.file_uploaded.connect(self.on_file_uploaded)
            dialog.exec()
        else:
            print(f"Error: Collection '{self.collection_name}' not found")
    
    def on_file_uploaded(self, file_data):
        """Handle file uploaded event"""
        print(f"File uploaded to collection: {file_data}")
        # Add file to table
        self.add_file_to_table(
            file_data.get('filename'),
            file_data.get('time'),
            file_data.get('extension')
        )
        self.file_uploaded.emit(file_data)
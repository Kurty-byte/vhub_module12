from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from ..controller.document_controller import DocumentController

class DeletedFileView(QWidget):
    def __init__(self, username, roles, primary_role, token, stack=None):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        
        # Initialize controller
        self.controller = DocumentController(username, roles, primary_role, token)

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

        # Load deleted files data using controller
        self.load_deleted_files()
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def create_actions_widget(self, filename, deleted_at=None):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        details_btn = QPushButton("Details")
        erase_btn = QPushButton("Erase")
        restore_btn = QPushButton("Restore")
        details_btn.clicked.connect(lambda: self.show_file_details(filename, deleted_at))
        erase_btn.clicked.connect(lambda: self.handle_permanent_delete(filename, deleted_at))
        restore_btn.clicked.connect(lambda: self.handle_restore(filename, deleted_at))
        layout.addWidget(details_btn)
        layout.addWidget(erase_btn)
        layout.addWidget(restore_btn)
        widget.setLayout(layout)
        return widget

    def go_back(self):
        print("Back button clicked")
        if self.stack:
            self.stack.setCurrentIndex(0)  # Assuming dashboard is at index 0

    def add_file_to_table(self, name, time, ext, deleted_at=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(time))
        self.table.setItem(row, 2, QTableWidgetItem(ext))
        actions_widget = self.create_actions_widget(name, deleted_at)
        self.table.setCellWidget(row, 3, actions_widget)

    def handle_item_clicked(self, item):
        if item.column() != 3:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            print(f"Deleted file row clicked: {filename}")
    
    def load_deleted_files(self):
        """Load and populate deleted files table"""
        # Clear existing rows
        self.table.setRowCount(0)
        
        # Get deleted files from controller
        files_data = self.controller.get_deleted_files()
        for file_data in files_data:
            self.add_file_to_table(
                file_data['filename'], 
                file_data.get('time', 'N/A'), 
                file_data['extension'],
                file_data.get('deleted_at')
            )
    
    def handle_restore(self, filename, deleted_at=None):
        """Restore a deleted file"""
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            'Confirm Restore',
            f"Are you sure you want to restore '{filename}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.controller.restore_file(filename, deleted_at)
            
            if success:
                QMessageBox.information(self, "Success", message)
                # Refresh the table
                self.load_deleted_files()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def handle_permanent_delete(self, filename, deleted_at=None):
        """Permanently delete a file"""
        # Confirmation dialog with warning
        reply = QMessageBox.warning(
            self, 
            'Confirm Permanent Delete',
            f"Are you sure you want to PERMANENTLY delete '{filename}'?\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.controller.permanent_delete_file(filename, deleted_at)
            
            if success:
                QMessageBox.information(self, "Success", message)
                # Refresh the table
                self.load_deleted_files()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def show_file_details(self, filename, deleted_at=None):
        """Show file details dialog"""
        # Get file details from deleted files
        files_data = self.controller.get_deleted_files()
        file_data = None
        
        for f in files_data:
            if f['filename'] == filename:
                if deleted_at is None or f.get('deleted_at') == deleted_at:
                    file_data = f
                    break
        
        if file_data:
            details_text = f"""
Filename: {file_data['filename']}
Extension: {file_data['extension']}
Category: {file_data.get('category', 'N/A')}
Uploaded by: {file_data.get('uploader', 'N/A')}
Upload Date: {file_data.get('uploaded_date', 'N/A')}
Deleted at: {file_data.get('deleted_at', 'N/A')}
Deleted by: {file_data.get('deleted_by', 'N/A')}
File Path: {file_data.get('file_path', 'N/A')}
            """
            QMessageBox.information(self, f"File Details - {filename}", details_text.strip())
        else:
            QMessageBox.warning(self, "Error", f"Could not find details for '{filename}'")

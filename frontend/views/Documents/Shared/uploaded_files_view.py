from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ..controller.document_controller import DocumentController
from ..utils.icon_utils import create_back_button, create_search_button, create_floating_add_button

class UploadedFilesView(QWidget):
    """
    Uploaded Files View - displays all uploaded files in a table
    Similar to DeletedFilesView but for active/uploaded files
    """
    file_deleted = pyqtSignal(dict)  # Signal to notify parent of file deletion
    file_uploaded = pyqtSignal(dict)  # Signal to notify parent of file upload
    
    def __init__(self, username, roles, primary_role, token, stack=None):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        
        # Initialize controller
        self.controller = DocumentController(username, roles, primary_role, token)

        self.stack: QStackedWidget = stack
        self.setWindowTitle("Uploaded Files")
        main_layout = QVBoxLayout()

        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = create_back_button(callback=self.go_back)

        header = QLabel("Uploaded Files")
        header.setFont(QFont("Arial", 16))
        
        # Add File button
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.handle_add_file)
        
        search_bar = QLineEdit()
        search_button = create_search_button(callback=lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search Uploaded Files...")
        search_bar.setMinimumWidth(200)
        
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(add_file_btn)
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        header_layout.addWidget(back_btn)
        main_layout.addLayout(header_layout)

        # Table for uploaded files
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Filename", "Time", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.handle_item_clicked)
        self.table.itemDoubleClicked.connect(self.handle_item_double_clicked)

        # Load uploaded files data using controller
        self.load_uploaded_files()
        main_layout.addWidget(self.table)

        # Floating Add Button (bottom-right corner)
        self.floating_add_btn = create_floating_add_button(callback=self.handle_add_file)
        self.floating_add_btn.setParent(self)
        self.position_floating_button()

        self.setLayout(main_layout)
    
    def resizeEvent(self, event):
        """Handle resize events to reposition floating button"""
        super().resizeEvent(event)
        self.position_floating_button()
    
    def position_floating_button(self):
        """Position the floating button in the bottom-right corner"""
        margin = 20
        button_size = self.floating_add_btn.size()
        x = self.width() - button_size.width() - margin
        y = self.height() - button_size.height() - margin
        self.floating_add_btn.move(x, y)
        self.floating_add_btn.raise_()  # Ensure button is on top

    def create_actions_widget(self, filename):
        """Create action buttons for each file row"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        download_btn = QPushButton("Download")
        delete_btn = QPushButton("Delete")
        
        download_btn.clicked.connect(lambda: self.handle_download(filename))
        delete_btn.clicked.connect(lambda: self.handle_delete(filename))
        
        layout.addWidget(download_btn)
        layout.addWidget(delete_btn)
        widget.setLayout(layout)
        return widget

    def go_back(self):
        """Navigate back to dashboard"""
        print("Back button clicked")
        if self.stack:
            self.stack.setCurrentIndex(0)  # Assuming dashboard is at index 0

    def add_file_to_table(self, name, time, ext):
        """Add a file row to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(time))
        actions_widget = self.create_actions_widget(name)
        self.table.setCellWidget(row, 2, actions_widget)

    def handle_item_clicked(self, item):
        """Handle table item click (not action buttons)"""
        if item.column() != 2:  # Not actions column (now column 2 instead of 3)
            filename = self.table.item(item.row(), 0).text()
            print(f"Uploaded file row clicked: {filename}")
    
    def handle_item_double_clicked(self, item):
        """Handle table item double-click - show file details dialog"""
        if item.column() != 2:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            self.show_file_details(filename)
    
    def load_uploaded_files(self):
        """Load and populate uploaded files table"""
        # Clear existing rows
        self.table.setRowCount(0)
        
        # Get uploaded files from controller
        files_data = self.controller.get_files()
        for file_data in files_data:
            self.add_file_to_table(
                file_data['filename'], 
                file_data.get('time', 'N/A'), 
                file_data['extension']
            )
    
    def handle_add_file(self):
        """Open the file upload dialog"""
        print("Add file clicked - Opening dialog")
        from .file_upload_dialog import FileUploadDialog
        dialog = FileUploadDialog(self, username=self.username, role=self.primary_role)
        dialog.file_uploaded.connect(self.on_file_uploaded)
        dialog.exec()
    
    def on_file_uploaded(self, file_data):
        """Handle file uploaded event - refresh the table and notify parent"""
        print(f"File uploaded: {file_data}")
        # Emit signal to notify parent (AdminDash)
        self.file_uploaded.emit(file_data)
        # Refresh the table
        self.load_uploaded_files()
    
    def handle_download(self, filename):
        """Handle file download"""
        print(f"Download file: {filename}")
        # TODO: Implement download functionality with controller
        QMessageBox.information(self, "Download", f"Downloading '{filename}'...\n\n(Download functionality to be implemented)")
    
    def handle_delete(self, filename):
        """Delete a file (move to trash/deleted files)"""
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            'Confirm Delete',
            f"Are you sure you want to delete '{filename}'?\n\nYou can restore it later from Deleted Files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get full file data before deletion
            files_data = self.controller.get_files()
            file_data = None
            for f in files_data:
                if f['filename'] == filename:
                    file_data = f
                    break
            
            success, message = self.controller.delete_file(filename)
            
            if success:
                QMessageBox.information(self, "Success", message)
                # Emit signal to notify parent with full file data (or at least filename)
                self.file_deleted.emit(file_data if file_data else {'filename': filename})
                # Refresh the table
                self.load_uploaded_files()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def show_file_details(self, filename):
        """Show file details dialog using custom widget"""
        # Get file details from uploaded files
        files_data = self.controller.get_files()
        file_data = None
        
        for f in files_data:
            if f['filename'] == filename:
                file_data = f
                break
        
        if file_data:
            from .file_details_dialog import FileDetailsDialog
            dialog = FileDetailsDialog(
                self, 
                file_data=file_data, 
                controller=self.controller,
                is_deleted=False
            )
            dialog.file_updated.connect(self.on_file_updated)
            dialog.file_deleted.connect(self.on_file_deleted_from_dialog)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", f"Could not find details for '{filename}'")
    
    def on_file_updated(self, file_data):
        """Handle file updated signal from details dialog"""
        print(f"File updated: {file_data}")
        # Refresh the table to show updated data
        self.load_uploaded_files()
    
    def on_file_deleted_from_dialog(self, file_data):
        """Handle file deleted signal from details dialog"""
        print(f"File deleted from dialog: {file_data}")
        # Emit signal to notify parent
        self.file_deleted.emit(file_data)
        # Refresh the table
        self.load_uploaded_files()

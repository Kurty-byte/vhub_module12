from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal
from ..controller.document_controller import DocumentController
from ..Mock.data_loader import get_collection_by_name
from ..utils.icon_utils import create_back_button, create_search_button, create_floating_add_button

class CollectionView(QWidget):
    file_accepted = pyqtSignal(str)
    file_rejected = pyqtSignal(str)
    file_uploaded = pyqtSignal(dict)
    file_deleted = pyqtSignal(dict)
    file_updated = pyqtSignal(dict)

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
        
        # Track file data for efficient incremental updates
        self.file_data_cache = {}  # {'filename': {'time': ..., 'extension': ..., 'row_index': ...}}
        
        main_layout = QVBoxLayout()

        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = create_back_button(callback=self.go_back)
        
        header = QLabel(f"{collection_name}" if collection_name else "Collection")
        header.setFont(QFont("Arial", 16))
        
        # Add File button
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.handle_add_file)

        search_bar = QLineEdit()
        search_button = create_search_button(callback=lambda: print("Search button clicked"))
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
        self.table.itemClicked.connect(self.handle_item_clicked)
        self.table.itemDoubleClicked.connect(self.handle_item_double_clicked)

        # Load collection data from JSON
        collection_data = get_collection_by_name(collection_name)
        if collection_data:
            files_data = collection_data.get('files', [])
            for idx, file_data in enumerate(files_data):
                self.add_file_to_table(file_data['filename'], file_data['time'], file_data['extension'])
                # Track file data in cache
                self.file_data_cache[file_data['filename']] = {
                    'time': file_data['time'],
                    'extension': file_data['extension'],
                    'row_index': idx
                }
        else:
            # Fallback if collection not found
            print(f"Warning: Collection '{collection_name}' not found in JSON data")
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
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        reject_btn = QPushButton("Reject")
        accept_btn = QPushButton("Accept")
        reject_btn.clicked.connect(lambda: print(f"Reject clicked for {filename}"))
        accept_btn.clicked.connect(lambda: print(f"Accept clicked for {filename}"))
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

    def handle_item_clicked(self, item):
        if item.column() != 3:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            print(f"File row clicked: {filename}")
    
    def handle_item_double_clicked(self, item):
        """Handle table item double-click - show file details dialog"""
        if item.column() != 3:  # Not actions column
            filename = self.table.item(item.row(), 0).text()
            self.show_file_details(filename)
    
    def show_file_details(self, filename):
        """Show file details dialog using custom widget"""
        # Get file details from collection
        collection_data = get_collection_by_name(self.collection_name)
        file_data = None
        
        if collection_data:
            files_data = collection_data.get('files', [])
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
            dialog.file_updated.connect(self.on_file_updated_from_dialog)
            dialog.file_deleted.connect(self.on_file_deleted_from_dialog)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", f"Could not find details for '{filename}'")
    
    def on_file_updated_from_dialog(self, file_data):
        """Handle file updated signal from details dialog"""
        print(f"File updated in collection: {file_data}")
        # Refresh collection files
        self.refresh_collection_files()
        # Forward signal to parent (AdminDash)
        self.file_updated.emit(file_data)
    
    def on_file_deleted_from_dialog(self, file_data):
        """Handle file deleted signal from details dialog"""
        print(f"File deleted from collection dialog: {file_data}")
        
        # Immediate UI update - remove file from table
        filename = file_data.get('filename')
        if filename and filename in self.file_data_cache:
            row_idx = self.file_data_cache[filename]['row_index']
            self.table.removeRow(row_idx)
            del self.file_data_cache[filename]
            self._rebuild_file_indices()
            print(f"Immediately removed file from collection UI: {filename}")
        
        # Then refresh to ensure consistency with data source
        self.refresh_collection_files()
        
        # Add collection name to file_data before forwarding
        file_data['collection_name'] = self.collection_name
        print(f"Added collection_name to deleted file_data: {self.collection_name}")
        
        # Forward signal to parent (AdminDash)
        self.file_deleted.emit(file_data)
    
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
        """Handle file uploaded event - incremental update"""
        print(f"File uploaded to collection: {file_data}")
        
        filename = file_data.get('filename')
        if not filename:
            # Fallback to full refresh if filename not provided
            self.refresh_collection_files()
            self.file_uploaded.emit(file_data)
            return
        
        # Check if file already exists
        if filename in self.file_data_cache:
            # Update existing file data
            row_idx = self.file_data_cache[filename]['row_index']
            self.table.item(row_idx, 0).setText(file_data.get('filename', filename))
            self.table.item(row_idx, 1).setText(file_data.get('time', ''))
            self.table.item(row_idx, 2).setText(file_data.get('extension', ''))
            
            # Update cache
            self.file_data_cache[filename]['time'] = file_data.get('time', '')
            self.file_data_cache[filename]['extension'] = file_data.get('extension', '')
            print(f"Updated existing file in collection UI: {filename}")
        else:
            # Add new file incrementally
            self.add_file_to_table(
                file_data.get('filename', ''),
                file_data.get('time', ''),
                file_data.get('extension', '')
            )
            
            # Add to cache
            self.file_data_cache[filename] = {
                'time': file_data.get('time', ''),
                'extension': file_data.get('extension', ''),
                'row_index': self.table.rowCount() - 1
            }
            print(f"Added new file to collection UI: {filename}")
        
        self.file_uploaded.emit(file_data)
    
    def refresh_collection_files(self):
        """Efficiently refresh collection files with incremental updates"""
        # Get fresh data from JSON
        collection_data = get_collection_by_name(self.collection_name)
        if not collection_data:
            print(f"Warning: Collection '{self.collection_name}' not found when refreshing")
            return
        
        files_data = collection_data.get('files', [])
        fresh_files = {f['filename']: f for f in files_data}
        
        current_filenames = set(self.file_data_cache.keys())
        fresh_filenames = set(fresh_files.keys())
        
        # Identify changes
        removed_files = current_filenames - fresh_filenames
        new_files = fresh_filenames - current_filenames
        existing_files = current_filenames & fresh_filenames
        
        # Check for modified files
        modified_files = set()
        for filename in existing_files:
            cached = self.file_data_cache[filename]
            fresh = fresh_files[filename]
            if cached['time'] != fresh['time'] or cached['extension'] != fresh['extension']:
                modified_files.add(filename)
        
        # Remove deleted files (sort by row index descending)
        for filename in sorted(removed_files, 
                              key=lambda f: self.file_data_cache[f]['row_index'], 
                              reverse=True):
            row_idx = self.file_data_cache[filename]['row_index']
            self.table.removeRow(row_idx)
            del self.file_data_cache[filename]
            print(f"Removed file from collection: {filename}")
        
        # Update modified files
        for filename in modified_files:
            row_idx = self.file_data_cache[filename]['row_index']
            fresh = fresh_files[filename]
            
            self.table.item(row_idx, 0).setText(fresh['filename'])
            self.table.item(row_idx, 1).setText(fresh['time'])
            self.table.item(row_idx, 2).setText(fresh['extension'])
            
            # Update cache
            self.file_data_cache[filename]['time'] = fresh['time']
            self.file_data_cache[filename]['extension'] = fresh['extension']
            print(f"Updated file in collection: {filename}")
        
        # Add new files
        for filename in new_files:
            fresh = fresh_files[filename]
            self.add_file_to_table(fresh['filename'], fresh['time'], fresh['extension'])
            
            # Add to cache
            self.file_data_cache[filename] = {
                'time': fresh['time'],
                'extension': fresh['extension'],
                'row_index': self.table.rowCount() - 1
            }
            print(f"Added file to collection: {filename}")
        
        # Rebuild row indices after removals
        if removed_files:
            self._rebuild_file_indices()
        
        print(f"Refreshed collection '{self.collection_name}' with incremental updates")
    
    def _rebuild_file_indices(self):
        """Rebuild row indices in file_data_cache after removals"""
        for row_idx in range(self.table.rowCount()):
            filename = self.table.item(row_idx, 0).text()
            if filename in self.file_data_cache:
                self.file_data_cache[filename]['row_index'] = row_idx
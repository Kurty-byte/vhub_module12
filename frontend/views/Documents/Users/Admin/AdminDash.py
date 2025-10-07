from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QFrame, QLineEdit, QScrollArea,
                             QTableView, QHeaderView,
                             QSizePolicy, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect
from ...controller.document_controller import DocumentController
from ...utils.icon_utils import create_menu_button, create_search_button, IconLoader

from .DonutWidget import DonutChartWidget


class AdminDash(QWidget):
    """
    Main Admin Dashboard Widget
    
    This widget displays a document management interface with:
    - Header with menu, title, and actions
    - Collections grid (horizontally scrollable)
    - Uploaded files list (scrollable table)
    - Storage usage chart
    
    Args: <This fields are necessary for the Router to recognize it as a widget>
        username (str): The logged-in user's username
        roles (list): List of user roles
        primary_role (str): The user's primary role
        token (str): Authentication token
    """
    
    def __init__(self, username, roles, primary_role, token):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        
        self.controller = DocumentController(username, roles, primary_role, token)

        # Track collection widgets for efficient updates
        self.collection_cards = {}  # {'collection_name': QFrame widget}
        self.collections_layout = None  # Reference to the layout
        self.selected_collection = None  # Track currently selected collection
        
        # Track file data for efficient updates
        self.file_data_cache = {}  # {'filename': {'time': ..., 'extension': ..., 'row_index': ...}}

        self.stack = QStackedWidget()

        self.dashboard_widget = QWidget()
        
        # Auto-cleanup old recycle bin files on startup
        self.auto_cleanup_recycle_bin()
        
        self.init_ui()

        self.stack.addWidget(self.dashboard_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        # self.refresh_storage_chart() #for testing only

        

    def init_ui(self):
        main_layout = QVBoxLayout()

        # ========== HEADER SECTION ==========
        header_layout = QHBoxLayout()
        
        # Menu button with hamburger icon - using utility
        menu_btn = create_menu_button(callback=lambda: print("Menu button clicked"))
        
        title = QLabel("Documents")
            
        # Changed from QLabel to QLineEdit for text input
        search_bar = QLineEdit()
        search_button = create_search_button(callback=lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search collections or files...")
        search_bar.setMinimumWidth(200)
        
        header_layout.addWidget(menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        
        main_layout.addLayout(header_layout)

        # ========== COLLECTIONS HEADER ==========
        collections_header = QHBoxLayout()
        collections_label = QLabel("Collections")
        add_collection_btn = QPushButton("Add Collection")
        add_collection_btn.clicked.connect(self.handle_add_collection)
        delete_collection_btn = QPushButton("Delete Collection")
        delete_collection_btn.clicked.connect(self.handle_delete_collection)
        upload_link = QPushButton("File Upload Requests")
        upload_link.clicked.connect(lambda: print("File Upload Requests clicked"))
        
        collections_header.addWidget(collections_label)
        collections_header.addStretch()
        collections_header.addWidget(add_collection_btn)
        collections_header.addWidget(delete_collection_btn)
        collections_header.addWidget(upload_link)
        
        main_layout.addLayout(collections_header)

        # ========== COLLECTIONS GRID ==========
        collections_scroll = QScrollArea()
        collections_scroll.setWidgetResizable(True)
        collections_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        collections_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        collections_scroll.setFixedHeight(130)

        collections_container = QWidget()
        self.collections_layout = QHBoxLayout()  # Store as instance variable
        self.collections_layout.setSpacing(25)
        
        # Load collections using controller and track them
        collections_data = self.controller.get_collections()
        for collection_data in collections_data:
            file_count = len(collection_data.get('files', []))  # Count files in collection
            collection = self.create_collection_card(
                collection_data['name'], 
                collection_data.get('icon', 'folder.png'),
                file_count=file_count
            )
            # Set up single click and double click handlers
            collection.mousePressEvent = self.make_collection_single_click_handler(collection_data['name'], collection)
            collection.mouseDoubleClickEvent = self.make_collection_double_click_handler(collection_data['name'])
            self.collection_cards[collection_data['name']] = collection  # Track widget
            self.collections_layout.addWidget(collection)
        
        self.collections_layout.addStretch()
        collections_container.setLayout(self.collections_layout)
        
        # Set the container as the scroll area's widget
        collections_scroll.setWidget(collections_container)
        main_layout.addWidget(collections_scroll)

        # ========== MAIN CONTENT AREA ==========
        content_layout = QHBoxLayout()

        # --- LEFT SIDE ---
        files_frame = QFrame()
        files_frame.setFrameShape(QFrame.Shape.Box)
        files_layout = QVBoxLayout()
        
        # Files header - now a clickable button
        files_header_layout = QHBoxLayout()
        files_title = QPushButton("Uploaded Files")
        files_title.setStyleSheet("text-align: left; font-weight: bold;")
        files_title.clicked.connect(self.handle_view_uploaded_files)
        delete_btn = QPushButton("Manage Deleted Files")
        delete_btn.clicked.connect(self.handle_manage_deleted_files)
        files_header_layout.addWidget(files_title)
        files_header_layout.addWidget(delete_btn)
        files_header_layout.addStretch()
        files_layout.addLayout(files_header_layout)

        # Create a table view and model for files
        self.files_table = QTableView()
        self.files_model = QStandardItemModel(0, 5)
        self.files_model.setHorizontalHeaderLabels(["Filename", "Upload Date", "Type", "Status", "Approval"])
        self.files_table.setModel(self.files_model)
        self.files_table.horizontalHeader().setStretchLastSection(True)
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.files_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.files_table.clicked.connect(self.handle_file_row_clicked)
        self.files_table.doubleClicked.connect(self.handle_file_row_double_clicked)
        
        # Connect model signals for automatic cache consistency
        self.files_model.rowsRemoved.connect(self._on_rows_removed)
        self.files_model.dataChanged.connect(self._on_data_changed)
        
        # Load file data using controller
        files_data = self.controller.get_files()

        # Populate and track files
        for idx, file_data in enumerate(files_data):
            status = file_data.get('status', 'available')
            approval = file_data.get('approval_status', 'pending')
            self.add_file_to_table(
                file_data['filename'], 
                file_data.get('uploaded_date', file_data.get('time', 'N/A')), 
                file_data['extension'],
                status,
                approval
            )
            # Track file data in cache
            self.file_data_cache[file_data['filename']] = {
                'uploaded_date': file_data.get('uploaded_date', file_data.get('time', 'N/A')),
                'extension': file_data['extension'],
                'status': status,
                'approval_status': approval,
                'row_index': idx
            }
        files_layout.addWidget(self.files_table)
        
        # New button at bottom right
        new_btn = QPushButton("+ New")
        new_btn.clicked.connect(self.handle_add_file)

        new_btn_layout = QHBoxLayout()
        new_btn_layout.addStretch()
        new_btn_layout.addWidget(new_btn)
        files_layout.addLayout(new_btn_layout)
        
        files_frame.setLayout(files_layout)
        content_layout.addWidget(files_frame, 6)

        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.Shape.Box)
        chart_layout = QVBoxLayout()
        
        # Load storage data using controller
        storage_data = self.controller.get_storage_info()
        
        # Create actual donut chart widget
        self.donut_chart = DonutChartWidget(
            used_percentage=storage_data['usage_percentage'],
            used_gb=storage_data['used_size_gb'],
            total_gb=storage_data['total_size_gb']
        )
        self.donut_chart.setMinimumHeight(250)
        chart_layout.addWidget(self.donut_chart)
        
        legend_layout = QVBoxLayout()
        
        used_row = QHBoxLayout()
        used_color = QLabel("●") 
        used_color.setStyleSheet("color: #084924; font-size: 16px; font-weight: bold;")  # for GREEN color
        used_label = QLabel("Used Storage")
        used_size = QLabel(f"Actual Size: {storage_data['used_size_gb']} GB")
        used_row.addWidget(used_color)
        used_row.addWidget(used_label)
        used_row.addStretch()
        used_row.addWidget(used_size)

        free_row = QHBoxLayout()
        free_color = QLabel("●")
        free_color.setStyleSheet("color: #E0E0E0; font-size: 16px; font-weight: bold;")  # this is ofr LIGHT GRAY colow
        free_label = QLabel("Free Space")
        free_size = QLabel(f"Unused Size: {storage_data['free_size_gb']} GB")
        free_row.addWidget(free_color)
        free_row.addWidget(free_label)
        free_row.addStretch()
        free_row.addWidget(free_size)
        
        
        legend_layout.addLayout(used_row)
        legend_layout.addLayout(free_row)
        
        chart_layout.addLayout(legend_layout)
        chart_frame.setLayout(chart_layout)
        content_layout.addWidget(chart_frame, 4)  # Takes 40% of width

        # Add content section to main layout
        main_layout.addLayout(content_layout)

        # Set the main layout for this widget
        self.dashboard_widget.setLayout(main_layout)

    def create_collection_card(self, name, icon_filename="folder.png", file_count=0):
        """
        Creates a single collection card widget
        
        Args:
            name (str): Display name for the collection
            icon_filename (str): Icon filename from Assets folder (default: "folder.png")
            file_count (int): Number of files in the collection
            
        Returns:
            QFrame: A frame containing the collection card UI
        """
        card = QFrame()
        card.setObjectName("collection_card")  # Set object name for targeted styling
        card.setFrameShape(QFrame.Shape.Box)
        card.setFixedSize(90, 90)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Vertical layout: icon stacked on top of label
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(2)  # Reduce spacing between elements
        
        # Load icon using IconLoader
        icon = IconLoader.create_icon_label(icon_filename, size=(32, 32), alignment=Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)  # Allow text wrapping if name is long
        
        # File count indicator
        count_label = QLabel(f"Files: {file_count}")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_label.setStyleSheet("color: gray; font-size: 10px;")
        count_label.setObjectName("file_count_label")  # Give it a unique name to find it later
        
        layout.addWidget(icon)
        layout.addWidget(label)
        layout.addWidget(count_label)
        card.setLayout(layout)
        
        return card

    def add_file_to_table(self, name, date, ext, status, approval):
        """
        Adds a file row to the files table (QTableView/QStandardItemModel)
        Args:
            name (str): Filename
            date (str): Upload date
            ext (str): File extension
            status (str): File status (available, soft_deleted, permanently_deleted)
            approval (str): Approval status (pending, accepted, rejected)
        """
        # Get emoji indicators
        status_emoji = self._get_status_emoji(status)
        approval_emoji = self._get_approval_emoji(approval)
        
        row = [
            QStandardItem(name), 
            QStandardItem(date), 
            QStandardItem(ext),
            QStandardItem(status_emoji),
            QStandardItem(approval_emoji)
        ]
        self.files_model.appendRow(row)

    def handle_file_row_clicked(self, index):
            # Get filename from the model
            filename = self.files_model.item(index.row(), 0).text()
            print(f"File row clicked: {filename}")
    
    def handle_file_row_double_clicked(self, index):
        """Handle file row double-click - show file details dialog"""
        filename = self.files_model.item(index.row(), 0).text()
        self.show_file_details(filename)
    
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
            from ...Shared.file_details_dialog import FileDetailsDialog
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
        print(f"File updated from dialog: {file_data}")
        # Refresh files table to show updated data
        self.refresh_files_table()
    
    def on_file_deleted_from_dialog(self, file_data):
        """Handle file deleted signal from details dialog"""
        print(f"File deleted from dialog: {file_data}")
        # Refresh files table
        self.refresh_files_table()
        
        # Update collection file counts
        print(f"DEBUG: file_data keys from dialog delete: {file_data.keys()}")
        collection_name = file_data.get('collection_name') or file_data.get('category')
        if collection_name:
            print(f"DEBUG: Updating specific collection: {collection_name}")
            self.update_collection_file_count(collection_name)
        else:
            print(f"DEBUG: No collection info, refreshing all collection counts")
            # If we can't determine which collection, refresh all
            self.refresh_all_collection_counts()

    def deleted_click_handler(self, event):
        def handler(event):
            print("Deleted Files clicked")
            from ...Shared.deleted_files_view import DeletedFileView
            deleted_file_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
            self.stack.addWidget(deleted_file_view)
            self.stack.setCurrentWidget(deleted_file_view)
        return handler
    
    def make_collection_single_click_handler(self, name, card_widget):
        """Handle single click on collection - highlight/select it"""
        def handler(event):
            print(f"Collection selected: {name}")
            # Clear previous selection
            if self.selected_collection and self.selected_collection != card_widget:
                self.selected_collection.setStyleSheet("QFrame#collection_card { border: 1px solid #cccccc; }")  # Reset to default subtle border
            
            # Highlight current selection with subtle border - only targets the outer card frame
            card_widget.setStyleSheet("QFrame#collection_card { border: 2px solid #0078d4; }")
            self.selected_collection = card_widget
        return handler
    
    def make_collection_double_click_handler(self, name):
        """Handle double click on collection - open it"""
        def handler(event):
            print(f"Collection opened: {name}")
            from ...Shared.collection_view import CollectionView
            collection_view = CollectionView(
                self.username,
                self.roles,
                self.primary_role,
                self.token,
                collection_name=name,
                stack=self.stack)

            # Connect all signals from collection view
            collection_view.file_uploaded.connect(self.on_file_uploaded)
            collection_view.file_deleted.connect(self.on_file_deleted)
            collection_view.file_updated.connect(self.on_file_updated_from_dialog)

            self.stack.addWidget(collection_view)
            self.stack.setCurrentWidget(collection_view)
        return handler
    
    def make_collection_click_handler(self, name):
        """Deprecated - kept for backward compatibility"""
        return self.make_collection_double_click_handler(name)

    def handle_add_collection(self):
        """Open the add collection dialog popup"""
        print("Add Collection clicked - Opening dialog")
        from ...Shared.add_collection_dialog import AddCollectionDialog
        dialog = AddCollectionDialog(self)
        dialog.collection_created.connect(self.on_collection_created)
        dialog.exec()  # Show modal dialog
    
    def handle_delete_collection(self):
        """Delete the currently selected collection"""
        if not self.selected_collection:
            QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select a collection first by clicking on it."
            )
            return
        
        # Find the collection name from the selected widget
        collection_name = None
        for name, widget in self.collection_cards.items():
            if widget == self.selected_collection:
                collection_name = name
                break
        
        if not collection_name:
            QMessageBox.warning(self, "Error", "Could not identify the selected collection.")
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Delete Collection',
            f"Are you sure you want to delete the collection '{collection_name}'?\n\n"
            f"All files in this collection will be moved to their respective categories.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete collection using controller
            success, message = self.controller.delete_collection(collection_name)
            
            if success:
                QMessageBox.information(self, "Success", message)
                
                # Remove the collection card from UI
                self.collections_layout.removeWidget(self.selected_collection)
                self.selected_collection.deleteLater()  # Schedule for deletion
                
                # Remove from tracking dictionary
                del self.collection_cards[collection_name]
                
                # Clear selection
                self.selected_collection = None
                
                print(f"Collection '{collection_name}' deleted successfully")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete collection: {message}")
    
    def handle_add_file(self):
        """Open the file upload dialog popup"""
        print("Add file clicked - Opening dialog")
        from ...Shared.file_upload_dialog import FileUploadDialog
        dialog = FileUploadDialog(self, username=self.username, role=self.primary_role)
        dialog.file_uploaded.connect(self.on_file_uploaded)
        dialog.exec()
    
    def on_collection_created(self, collection_data):
        """Handle collection created event - incremental update"""
        print(f"Collection created: {collection_data}")
        
        collection_name = collection_data.get('name')
        if not collection_name:
            # Fallback to full refresh if name not provided
            self.refresh_collections()
            return
        
        # Check if collection already exists (avoid duplicates)
        if collection_name in self.collection_cards:
            print(f"Collection '{collection_name}' already exists, skipping.")
            return

        # Add single collection instead of full refresh
        file_count = len(collection_data.get('files', []))
        card = self.create_collection_card(
            collection_name, 
            collection_data.get('icon', 'folder.png'),
            file_count=file_count
        )
        # Set up single click and double click handlers
        card.mousePressEvent = self.make_collection_single_click_handler(collection_name, card)
        card.mouseDoubleClickEvent = self.make_collection_double_click_handler(collection_name)
        self.collection_cards[collection_name] = card
        
        # Insert before the stretch (which is at the last position)
        insert_position = self.collections_layout.count() - 1
        self.collections_layout.insertWidget(insert_position, card)
        print(f"Added new collection to UI: {collection_name}")
    
    def on_file_uploaded(self, file_data):
        """Handle file uploaded event - incremental update"""
        print(f"File uploaded: {file_data}")
        
        filename = file_data.get('filename')
        if not filename:
            # Fallback to full refresh if filename not provided
            self.refresh_files_table()
            return
        
        # Check if file already exists
        if filename in self.file_data_cache:
            # Update existing file data
            row_idx = self.file_data_cache[filename]['row_index']
            status = file_data.get('status', 'available')
            approval = file_data.get('approval_status', 'pending')
            
            self.files_model.item(row_idx, 0).setText(file_data.get('filename', filename))
            self.files_model.item(row_idx, 1).setText(file_data.get('uploaded_date', file_data.get('time', '')))
            self.files_model.item(row_idx, 2).setText(file_data.get('extension', ''))
            self.files_model.item(row_idx, 3).setText(self._get_status_emoji(status))
            self.files_model.item(row_idx, 4).setText(self._get_approval_emoji(approval))
            
            # Update cache
            self.file_data_cache[filename]['uploaded_date'] = file_data.get('uploaded_date', file_data.get('time', ''))
            self.file_data_cache[filename]['extension'] = file_data.get('extension', '')
            self.file_data_cache[filename]['status'] = status
            self.file_data_cache[filename]['approval_status'] = approval
            print(f"Updated existing file in UI: {filename}")
        else:
            # Add new file
            status = file_data.get('status', 'available')
            approval = file_data.get('approval_status', 'pending')
            
            self.add_file_to_table(
                file_data.get('filename', ''),
                file_data.get('uploaded_date', file_data.get('time', '')),
                file_data.get('extension', ''),
                status,
                approval
            )
            
            # Add to cache
            self.file_data_cache[filename] = {
                'uploaded_date': file_data.get('uploaded_date', file_data.get('time', '')),
                'extension': file_data.get('extension', ''),
                'status': status,
                'approval_status': approval,
                'row_index': self.files_model.rowCount() - 1
            }
            print(f"Added new file to UI: {filename}")
        
        # Update collection file count if file was added to a collection
        print(f"DEBUG: file_data keys: {file_data.keys()}")
        print(f"DEBUG: collection_name = {file_data.get('collection_name')}")
        print(f"DEBUG: collection_id = {file_data.get('collection_id')}")

        collection_name = file_data.get('collection_name')
        if collection_name:
            print(f"DEBUG: Updating count for collection: {collection_name}")
            self.update_collection_file_count(collection_name)
        else:
            print(f"DEBUG: No collection_name found in file_data")
    
    def refresh_collections(self):
        """Efficiently refresh the collections grid with incremental updates"""
        if not self.collections_layout:
            return
        
        # Get fresh data from controller
        collections_data = self.controller.get_collections()
        fresh_collection_names = {col['name'] for col in collections_data}
        current_collection_names = set(self.collection_cards.keys())
        
        # Identify changes
        removed_collections = current_collection_names - fresh_collection_names
        new_collections = [col for col in collections_data if col['name'] not in current_collection_names]
        
        # Remove deleted collections
        for removed_name in removed_collections:
            widget = self.collection_cards.pop(removed_name)
            self.collections_layout.removeWidget(widget)
            widget.deleteLater()
            print(f"Removed collection: {removed_name}")
        
        # Add new collections (insert before the stretch item)
        for new_collection_data in new_collections:
            card = self.create_collection_card(
                new_collection_data['name'], 
                new_collection_data.get('icon', 'folder.png')
            )
            card.mousePressEvent = self.make_collection_click_handler(new_collection_data['name'])
            self.collection_cards[new_collection_data['name']] = card
            
            # Insert before the stretch (which is at the last position)
            insert_position = self.collections_layout.count() - 1
            self.collections_layout.insertWidget(insert_position, card)
            print(f"Added collection: {new_collection_data['name']}")
    
    def refresh_files_table(self):
        """Efficiently refresh the uploaded files table with incremental updates"""
        # Get fresh data from controller
        files_data = self.controller.get_files()
        fresh_files = {f['filename']: f for f in files_data}
        
        current_filenames = set(self.file_data_cache.keys())
        fresh_filenames = set(fresh_files.keys())
        
        # Identify changes
        removed_files = current_filenames - fresh_filenames
        new_files = fresh_filenames - current_filenames
        existing_files = current_filenames & fresh_filenames
        
        # Check for modified files (data changed but file still exists)
        modified_files = set()
        for filename in existing_files:
            cached = self.file_data_cache[filename]
            fresh = fresh_files[filename]
            if (cached.get('uploaded_date') != fresh.get('uploaded_date', fresh.get('time', '')) or 
                cached.get('extension') != fresh.get('extension') or
                cached.get('status') != fresh.get('status', 'available') or
                cached.get('approval_status') != fresh.get('approval_status', 'pending')):
                modified_files.add(filename)
        
        # Remove deleted files (sort by row index descending to avoid index shifting issues)
        for filename in sorted(removed_files, 
                              key=lambda f: self.file_data_cache[f]['row_index'], 
                              reverse=True):
            row_idx = self.file_data_cache[filename]['row_index']
            self.files_model.removeRow(row_idx)
            del self.file_data_cache[filename]
            print(f"Removed file: {filename}")
        
        # Update modified files
        for filename in modified_files:
            row_idx = self.file_data_cache[filename]['row_index']
            fresh = fresh_files[filename]
            status = fresh.get('status', 'available')
            approval = fresh.get('approval_status', 'pending')
            
            self.files_model.item(row_idx, 0).setText(fresh['filename'])
            self.files_model.item(row_idx, 1).setText(fresh.get('uploaded_date', fresh.get('time', '')))
            self.files_model.item(row_idx, 2).setText(fresh['extension'])
            self.files_model.item(row_idx, 3).setText(self._get_status_emoji(status))
            self.files_model.item(row_idx, 4).setText(self._get_approval_emoji(approval))
            
            # Update cache
            self.file_data_cache[filename]['uploaded_date'] = fresh.get('uploaded_date', fresh.get('time', ''))
            self.file_data_cache[filename]['extension'] = fresh['extension']
            self.file_data_cache[filename]['status'] = status
            self.file_data_cache[filename]['approval_status'] = approval
            print(f"Updated file: {filename}")
        
        # Add new files
        for filename in new_files:
            fresh = fresh_files[filename]
            status = fresh.get('status', 'available')
            approval = fresh.get('approval_status', 'pending')
            
            self.add_file_to_table(
                fresh['filename'], 
                fresh.get('uploaded_date', fresh.get('time', '')), 
                fresh['extension'],
                status,
                approval
            )
            
            # Add to cache with current row index
            self.file_data_cache[filename] = {
                'uploaded_date': fresh.get('uploaded_date', fresh.get('time', '')),
                'extension': fresh['extension'],
                'status': status,
                'approval_status': approval,
                'row_index': self.files_model.rowCount() - 1
            }
            print(f"Added file: {filename}")
        
        # Rebuild row indices after all changes (removals shift indices)
        if removed_files:
            self._rebuild_file_indices()
    
    def handle_manage_deleted_files(self):
        print("Manage Deleted Files clicked")
        from ...Shared.deleted_files_view import DeletedFileView
        deleted_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
        deleted_view.file_restored.connect(self.on_file_restored)
        self.stack.addWidget(deleted_view)
        self.stack.setCurrentWidget(deleted_view)
    
    def handle_view_uploaded_files(self):
        """Open the uploaded files view"""
        print("View Uploaded Files clicked")
        from ...Shared.uploaded_files_view import UploadedFilesView
        uploaded_view = UploadedFilesView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
        uploaded_view.file_deleted.connect(self.on_file_deleted)
        uploaded_view.file_uploaded.connect(self.on_file_uploaded)
        self.stack.addWidget(uploaded_view)
        self.stack.setCurrentWidget(uploaded_view)
    
    def on_file_deleted(self, file_data):
        """Handle file deleted event - refresh the files table and update collection count"""
        print(f"File deleted: {file_data}")
        self.refresh_files_table()
        
        # Update collection file count if file was deleted from a collection
        print(f"DEBUG: file_data keys on delete: {file_data.keys()}")
        print(f"DEBUG: collection_name = {file_data.get('collection_name')}")
        print(f"DEBUG: category = {file_data.get('category')}")
        
        # Try to get collection name from file_data
        collection_name = file_data.get('collection_name') or file_data.get('category')
        if collection_name:
            print(f"DEBUG: Updating count for collection after deletion: {collection_name}")
            self.update_collection_file_count(collection_name)
        else:
            print(f"DEBUG: No collection_name found in deleted file_data, updating all collections")
            # If we can't determine which collection, refresh all collection counts
            self.refresh_all_collection_counts()
    
    def on_file_restored(self, file_data):
        """Handle file restored event - refresh the files table and update collection counts"""
        print(f"File restored: {file_data}")
        self.refresh_files_table()
        
        # Update collection file counts - file was restored back to its original collections
        print(f"DEBUG: file_data keys on restore: {file_data.keys()}")
        print(f"DEBUG: _original_collections = {file_data.get('_original_collections')}")
        
        # Check for original collections (stored during deletion)
        original_collections = file_data.get('_original_collections', [])
        if original_collections:
            print(f"DEBUG: Updating counts for restored collections: {original_collections}")
            for collection_name in original_collections:
                self.update_collection_file_count(collection_name)
        else:
            # Fallback: check for single collection name
            collection_name = file_data.get('collection_name') or file_data.get('category')
            if collection_name:
                print(f"DEBUG: Updating count for single collection: {collection_name}")
                self.update_collection_file_count(collection_name)
            else:
                print(f"DEBUG: No collection info found, refreshing all collection counts")
                # If we can't determine which collections, refresh all
                self.refresh_all_collection_counts()
    
    def auto_cleanup_recycle_bin(self):
        """Automatically cleanup old files from recycle bin on startup"""
        try:
            success, message, count = self.controller.cleanup_old_recycle_bin_files(days=15)
            if success and count > 0:
                print(f"Auto-cleanup: {message}")
            elif not success:
                print(f"Auto-cleanup failed: {message}")
        except Exception as e:
            print(f"Error during auto-cleanup: {str(e)}")
    
    def _rebuild_file_indices(self):
        """
        Rebuild row indices in file_data_cache after removals.
        This ensures cache indices match actual model row positions.
        """
        # Iterate through model rows and update cache with correct indices
        for row_idx in range(self.files_model.rowCount()):
            filename = self.files_model.item(row_idx, 0).text()
            if filename in self.file_data_cache:
                self.file_data_cache[filename]['row_index'] = row_idx
    
    def _on_rows_removed(self, parent, first, last):
        """
        Auto-update cache when rows are removed from model.
        Connected to files_model.rowsRemoved signal.
        """
        self._rebuild_file_indices()
    
    def _on_data_changed(self, topLeft, bottomRight):
        """
        Auto-sync cache when data changes in model.
        Connected to files_model.dataChanged signal.
        """
        for row in range(topLeft.row(), bottomRight.row() + 1):
            filename = self.files_model.item(row, 0).text()
            if filename in self.file_data_cache:
                self.file_data_cache[filename]['uploaded_date'] = self.files_model.item(row, 1).text()
                self.file_data_cache[filename]['extension'] = self.files_model.item(row, 2).text()
    
    def _get_status_emoji(self, status):
        """
        Get emoji indicator for file status.
        
        Args:
            status (str): File status
            
        Returns:
            str: Emoji + status text
        """
        status_map = {
            'available': '🟢 Available',
            'soft_deleted': '🟡 Deleted',
            'permanently_deleted': '🔴 Permanently Deleted'
        }
        return status_map.get(status, '⚪ Unknown')
    
    def _get_approval_emoji(self, approval):
        """
        Get emoji indicator for approval status.
        
        Args:
            approval (str): Approval status
            
        Returns:
            str: Emoji + approval text
        """
        approval_map = {
            'pending': '🟡 Pending',
            'accepted': '🟢 Accepted',
            'rejected': '🔴 Rejected'
        }
        return approval_map.get(approval, '⚪ Unknown')
    
    def update_collection_file_count(self, collection_name):
        """
        Update the file count indicator on a specific collection card
        
        Args:
            collection_name (str): Name of the collection to update
        """
        if collection_name not in self.collection_cards:
            print(f"Collection '{collection_name}' not found in cache")
            return
        
        # Get fresh data from controller
        collections_data = self.controller.get_collections()
        collection_data = next((c for c in collections_data if c['name'] == collection_name), None)
        
        if not collection_data:
            print(f"Collection '{collection_name}' not found in data")
            return
        
        # Find the count label in the card widget
        card = self.collection_cards[collection_name]
        count_label = card.findChild(QLabel, "file_count_label")
        
        if count_label:
            file_count = len(collection_data.get('files', []))
            count_label.setText(f"Files: {file_count}")
            print(f"Updated file count for '{collection_name}': {file_count}")
        else:
            print(f"Count label not found for '{collection_name}'")
    
    def refresh_all_collection_counts(self):
        """
        Refresh file counts for all collection cards.
        
        Useful when we don't know which specific collection changed.
        """
        print("Refreshing all collection file counts...")
        
        # Get fresh data from controller
        collections_data = self.controller.get_collections()
        
        # Update each collection card
        for collection_data in collections_data:
            collection_name = collection_data.get('name')
            if collection_name and collection_name in self.collection_cards:
                card = self.collection_cards[collection_name]
                count_label = card.findChild(QLabel, "file_count_label")
                
                if count_label:
                    file_count = len(collection_data.get('files', []))
                    count_label.setText(f"Files: {file_count}")
                    print(f"  - Updated '{collection_name}': {file_count} files")
        
        print("All collection counts refreshed.")
        
        
    def refresh_storage_chart(self):
        """
        refresh the storage chart with updated data from the controller
        u can call this when
        
            after uploading files and after file deletions
            (and maybe after some operations that updates
            the storage of the vault)
        
        """
        storage_data = self.controller.get_storage_info()
        if hasattr(self, 'donut_chart'):
            self.donut_chart.update_data(
                used_percentage=storage_data['usage_percentage'],
                # used_percentage=25, # for TESTING (uncomment this to show a percentage)
                used_gb=storage_data['used_size_gb'],
                total_gb=storage_data['total_size_gb']
            )

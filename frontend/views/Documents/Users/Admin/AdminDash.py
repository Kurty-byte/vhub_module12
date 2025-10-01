from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QFrame, QLineEdit, QScrollArea,
                             QTableView, QHeaderView,
                             QSizePolicy, QStackedWidget, QMessageBox)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from ...controller.document_controller import DocumentController
from ...utils.icon_utils import create_menu_button, create_search_button, IconLoader


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

        self.stack = QStackedWidget()

        self.dashboard_widget = QWidget()
        self.init_ui()

        self.stack.addWidget(self.dashboard_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # ========== HEADER SECTION ==========
        header_layout = QHBoxLayout()
        
        # Menu button with hamburger icon - using utility
        menu_btn = create_menu_button(callback=lambda: print("Menu button clicked"))
        
        title = QLabel("Documents")
        add_collection_btn = QPushButton("Add Collection")
        add_collection_btn.clicked.connect(self.handle_add_collection)
        delete_btn = QPushButton("Manage Deleted Files")
        delete_btn.clicked.connect(self.handle_manage_deleted_files)
            
        # Changed from QLabel to QLineEdit for text input
        search_bar = QLineEdit()
        search_button = create_search_button(callback=lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search Organization...")
        search_bar.setMinimumWidth(200)
        
        header_layout.addWidget(menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_collection_btn)
        header_layout.addWidget(delete_btn)
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        
        main_layout.addLayout(header_layout)

        # ========== COLLECTIONS HEADER ==========
        collections_header = QHBoxLayout()
        collections_label = QLabel("Collections")
        upload_link = QPushButton("File Upload Requests")
        upload_link.clicked.connect(lambda: print("File Upload Requests clicked"))
        
        collections_header.addWidget(collections_label)
        collections_header.addStretch()
        collections_header.addWidget(upload_link)
        
        main_layout.addLayout(collections_header)

        # ========== COLLECTIONS GRID ==========
        collections_scroll = QScrollArea()
        collections_scroll.setWidgetResizable(True)
        collections_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        collections_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        collections_scroll.setFixedHeight(130)

        collections_container = QWidget()
        collections_layout = QHBoxLayout()
        collections_layout.setSpacing(25)
        
        # Load collections using controller
        collections_data = self.controller.get_collections()
        for collection_data in collections_data:
            collection = self.create_collection_card(collection_data['name'], collection_data.get('icon', 'folder.png'))
            collection.mousePressEvent = self.make_collection_click_handler(collection_data['name'])
            collections_layout.addWidget(collection)
        
        collections_layout.addStretch()
        collections_container.setLayout(collections_layout)
        
        # Set the container as the scroll area's widget
        collections_scroll.setWidget(collections_container)
        main_layout.addWidget(collections_scroll)

        # ========== MAIN CONTENT AREA ==========
        content_layout = QHBoxLayout()

        # --- LEFT SIDE ---
        files_frame = QFrame()
        files_frame.setFrameShape(QFrame.Shape.Box)
        files_layout = QVBoxLayout()
        
        # Files header
        files_title = QLabel("Uploaded Files")
        files_layout.addWidget(files_title)

        # Create a table view and model for files
        self.files_table = QTableView()
        self.files_model = QStandardItemModel(0, 3)
        self.files_model.setHorizontalHeaderLabels(["Filename", "Time", "Extension"])
        self.files_table.setModel(self.files_model)
        self.files_table.horizontalHeader().setStretchLastSection(True)
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.files_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.files_table.clicked.connect(self.handle_file_row_clicked)
        
        # Load file data using controller
        files_data = self.controller.get_files()

        # Populate
        for file_data in files_data:
            self.add_file_to_table(file_data['filename'], file_data['time'], file_data['extension'])
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
        
        # Placeholder for donut chart (will be custom widget later)
        chart_placeholder = QLabel(f"{storage_data['usage_percentage']}%\nTotal Size: {storage_data['total_size_gb']} GB")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setMinimumHeight(250)
        chart_layout.addWidget(chart_placeholder)
        
        legend_layout = QVBoxLayout()
        
        used_row = QHBoxLayout()
        used_color = QLabel("■") 
        used_label = QLabel("Used Storage")
        used_size = QLabel(f"Actual Size: {storage_data['used_size_gb']} GB")
        used_row.addWidget(used_color)
        used_row.addWidget(used_label)
        used_row.addStretch()
        used_row.addWidget(used_size)

        free_row = QHBoxLayout()
        free_color = QLabel("□")
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

    def create_collection_card(self, name, icon_filename="folder.png"):
        """
        Creates a single collection card widget
        
        Args:
            name (str): Display name for the collection
            icon_filename (str): Icon filename from Assets folder (default: "folder.png")
            
        Returns:
            QFrame: A frame containing the collection card UI
        """
        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)  # Add border for visibility
        card.setFixedSize(90, 90)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Vertical layout: icon stacked on top of label
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Load icon using IconLoader
        icon = IconLoader.create_icon_label(icon_filename, size=(32, 32), alignment=Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon)
        layout.addWidget(label)
        card.setLayout(layout)
        
        return card

    def add_file_to_table(self, name, time, ext):
        """
        Adds a file row to the files table (QTableView/QStandardItemModel)
        Args:
            name (str): Filename
            time (str): Upload time
            ext (str): File extension
        """
        row = [QStandardItem(name), QStandardItem(time), QStandardItem(ext)]
        self.files_model.appendRow(row)

    def handle_file_row_clicked(self, index):
            # Get filename from the model
            filename = self.files_model.item(index.row(), 0).text()
            print(f"File row clicked: {filename}")

    def deleted_click_handler(self, event):
        def handler(event):
            print("Deleted Files clicked")
            from ...Shared.deleted_files_view import DeletedFileView
            deleted_file_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
            self.stack.addWidget(deleted_file_view)
            self.stack.setCurrentWidget(deleted_file_view)
        return handler
    
    def make_collection_click_handler(self, name):
        def handler(event):
            print(f"Collection clicked: {name}")
            from ...Shared.collection_view import CollectionView
            collection_view = CollectionView(
                self.username,
                self.roles,
                self.primary_role,
                self.token,
                collection_name=name,
                stack=self.stack)

            collection_view.file_uploaded.connect(self.on_file_uploaded)

            self.stack.addWidget(collection_view)
            self.stack.setCurrentWidget(collection_view)
        return handler

    def handle_add_collection(self):
        """Open the add collection dialog popup"""
        print("Add Collection clicked - Opening dialog")
        from ...Shared.add_collection_dialog import AddCollectionDialog
        dialog = AddCollectionDialog(self)
        dialog.collection_created.connect(self.on_collection_created)
        dialog.exec()  # Show modal dialog
    
    def handle_add_file(self):
        """Open the file upload dialog popup"""
        print("Add file clicked - Opening dialog")
        from ...Shared.file_upload_dialog import FileUploadDialog
        dialog = FileUploadDialog(self, username=self.username, role=self.primary_role)
        dialog.file_uploaded.connect(self.on_file_uploaded)
        dialog.exec()
    
    def on_collection_created(self, collection_data):
        """Handle collection created event"""
        print(f"Collection created: {collection_data}")
        # Refresh the collections display
        self.refresh_collections()
    
    def on_file_uploaded(self, file_data):
        """Handle file uploaded event"""
        print(f"File uploaded: {file_data}")
        # Refresh the files table
        self.refresh_files_table()
    
    def refresh_collections(self):
        """Reload and refresh the collections grid"""
        # Find the collections scroll area widget
        collections_scroll = self.dashboard_widget.findChild(QScrollArea)
        if collections_scroll:
            # Get the container widget
            container = collections_scroll.widget()
            if container:
                # Clear existing layout
                layout = container.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    
                    # Reload collections using controller
                    collections_data = self.controller.get_collections()
                    for collection_data in collections_data:
                        collection = self.create_collection_card(collection_data['name'], collection_data.get('icon', 'folder.png'))
                        collection.mousePressEvent = self.make_collection_click_handler(collection_data['name'])
                        layout.addWidget(collection)
                    
                    layout.addStretch()
    
    def refresh_files_table(self):
        """Reload and refresh the uploaded files table"""
        # Clear existing rows
        self.files_model.removeRows(0, self.files_model.rowCount())
        
        # Reload files using controller
        files_data = self.controller.get_files()
        for file_data in files_data:
            self.add_file_to_table(file_data['filename'], file_data['time'], file_data['extension'])
    
    def handle_manage_deleted_files(self):
        print("Manage Deleted Files clicked")
        from ...Shared.deleted_files_view import DeletedFileView
        deleted_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
        self.stack.addWidget(deleted_view)
        self.stack.setCurrentWidget(deleted_view)
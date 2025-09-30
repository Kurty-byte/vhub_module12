from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QFrame, QLineEdit, QScrollArea,
                             QTableView, QHeaderView,
                             QSizePolicy, QStackedWidget)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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

        self.stack = QStackedWidget()

        self.dashboard_widget = QWidget()
        self.setup_dashboard()

        self.stack.addWidget(self.dashboard_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

    def setup_dashboard(self):
        main_layout = QVBoxLayout()

        # ========== HEADER SECTION ==========
        header_layout = QHBoxLayout()
        
        menu_btn = QLabel("☰ Menu")
        title = QLabel("Documents")
        add_btn = QPushButton("Add file")
        add_btn.clicked.connect(lambda event: print("Add file clicked"))
        delete_btn = QPushButton("Manage Deleted Files")
        delete_btn.clicked.connect(self.handle_manage_deleted_files)
            
        # Changed from QLabel to QLineEdit for text input
        search_bar = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: print("Search button clicked"))
        search_bar.setPlaceholderText("Search Organization...")
        search_bar.setMinimumWidth(200)
        
        header_layout.addWidget(menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(delete_btn)
        header_layout.addWidget(search_bar)
        header_layout.addWidget(search_button)
        
        main_layout.addLayout(header_layout)

        # ========== COLLECTIONS HEADER ==========
        collections_header = QHBoxLayout()
        collections_label = QLabel("Collections")
        upload_link = QLabel("File Upload Requests")
        upload_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        upload_link.mousePressEvent = lambda event: print("Upload link clicked")
        
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
        
        for i in range(1,20):
            collection = self.create_collection_card(f"Collection {i}")
            collection.mousePressEvent = self.make_collection_click_handler(f"Collection {i}")
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
        
        # Sample file data(to json)
        files_data = [
            ("Request Letter", "11:55 pm", "pdf"),
            ("Weaver", "1:00 pm", ".docx"),
            ("Memorandum", "7:00 am", "pdf"),
            ("Syllabus", "12:00 pm", "pdf"),
            ("Budget Report", "3:30 pm", "xlsx"),
            ("Meeting Notes", "9:15 am", "pdf"),
            ("Presentation", "2:45 pm", "pptx"),
            ("Contract", "11:00 am", "pdf"),
        ]

        # Populate
        for name, time, ext in files_data:
            self.add_file_to_table(name, time, ext)
        files_layout.addWidget(self.files_table)
        
        # New button at bottom right
        new_btn = QPushButton("+ New")
        new_btn.clicked.connect(lambda: print("New button clicked"))

        new_btn_layout = QHBoxLayout()
        new_btn_layout.addStretch()
        new_btn_layout.addWidget(new_btn)
        files_layout.addLayout(new_btn_layout)
        
        files_frame.setLayout(files_layout)
        content_layout.addWidget(files_frame, 6)

        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.Shape.Box)
        chart_layout = QVBoxLayout()
        
        # Placeholder for donut chart (will be custom widget later)
        chart_placeholder = QLabel("75%\nTotal Size: 24.5 GB")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setMinimumHeight(250)
        chart_layout.addWidget(chart_placeholder)
        
        legend_layout = QVBoxLayout()
        
        used_row = QHBoxLayout()
        used_color = QLabel("■") 
        used_label = QLabel("Used Storage")
        used_size = QLabel("Actual Size: 18.37 GB")
        used_row.addWidget(used_color)
        used_row.addWidget(used_label)
        used_row.addStretch()
        used_row.addWidget(used_size)

        free_row = QHBoxLayout()
        free_color = QLabel("□")
        free_label = QLabel("Free Space")
        free_size = QLabel("Unused Size: 6.12 GB")
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

    def make_collection_click_handler(self, name):
        def handler(event):
            print(f"Collection clicked: {name}")
            from ...Shared.CollectionView import CollectionView
            collection_view = CollectionView(self.username, self.roles, self.primary_role, self.token, collection_name=name, stack=self.stack)
            self.stack.addWidget(collection_view)
            self.stack.setCurrentWidget(collection_view)
        return handler

    def handle_manage_deleted_files(self):
        print("Manage Deleted Files clicked")
        from ...Shared.DeletedFileView import DeletedFileView
        deleted_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
        self.stack.addWidget(deleted_view)
        self.stack.setCurrentWidget(deleted_view)
    
    def deleted_click_handler(self, event):
        def handler(event):
            print("Deleted Files clicked")
            from ...Shared.DeletedFileView import DeletedFileView
            deleted_file_view = DeletedFileView(self.username, self.roles, self.primary_role, self.token, stack=self.stack)
            self.stack.addWidget(deleted_file_view)
            self.stack.setCurrentWidget(deleted_file_view)
        return handler

    def create_collection_card(self, name):
        """
        Creates a single collection card widget
        
        Layout structure:
        ┌─────────┐
        │  Icon   │
        │  Name   │
        └─────────┘
        
        Args:
            name (str): Display name for the collection
            
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
        
        icon = QLabel("📄")  # Placeholder icon
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
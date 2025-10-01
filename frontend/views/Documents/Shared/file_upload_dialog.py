from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QTextEdit, QFrame,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import datetime
import os
from ..utils.icon_utils import IconLoader


class FileUploadDialog(QDialog):
    """
    File Upload Dialog - Modal popup for uploading files
    
    This dialog provides a form interface for uploading files with:
    - File/Folder selection buttons
    - Editable filename
    - Upload date display
    - Category and Organization dropdowns
    - File description text area
    - Upload action button
    
    Signals:
        file_uploaded: Emitted when a file is successfully uploaded
    
    Args:
        parent (QWidget): Parent widget (typically AdminDash)
        collection_id (int, optional): Pre-select collection for file upload
    """
    
    # Signal emitted when file is uploaded
    file_uploaded = pyqtSignal(dict)
    
    def __init__(self, parent=None, collection_id=None, username=None, role=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Upload File")
        self.setFixedSize(400, 550)
        
        self.selected_file_path = None
        self.collection_id = collection_id
        self.username = username  # Store username
        self.role = role  # Store role (can be "student-org_officer")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI components"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # ========== CLOSE BUTTON (Top Right) ==========
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        main_layout.addLayout(close_layout)
        
        # ========== FILE ICON ==========
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        file_icon = IconLoader.create_icon_label("document.png", size=(64, 64), alignment=Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(file_icon)
        main_layout.addLayout(icon_layout)
        
        # ========== FILE SELECTION BUTTONS ==========
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.handle_select_folder)
        
        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.handle_select_file)
        
        button_layout.addWidget(select_folder_btn)
        button_layout.addWidget(select_file_btn)
        main_layout.addLayout(button_layout)
        
        # ========== FILENAME (Editable) ==========
        filename_layout = QHBoxLayout()
        filename_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.filename_input = QLineEdit("File 1.docx")
        self.filename_input.setMaximumWidth(200)

        edit_icon_button = IconLoader.create_icon_button(
            "pencil.png", 
            size=(16, 16), 
            button_size=(24, 24),
            flat=True,
            callback=lambda: self.filename_input.setFocus()
        )
        edit_icon_button.clicked.connect(self.handle_edit_filename)
        
        filename_layout.addWidget(self.filename_input)
        filename_layout.addWidget(edit_icon_button)
        main_layout.addLayout(filename_layout)
        
        # ========== UPLOAD DATE ==========
        date_layout = QHBoxLayout()
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        upload_date = QLabel(f"Uploaded on {datetime.datetime.now().strftime('%m/%d/%Y')}")
        date_layout.addWidget(upload_date)
        main_layout.addLayout(date_layout)
        
        # ========== CATEGORY DROPDOWN ==========
        category_layout = QHBoxLayout()
        category_label = QLabel("Category")
        category_label.setFixedWidth(100)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["None", "Syllabus", "Memo", "Forms", "Report", "Other"])
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        main_layout.addLayout(category_layout)
        
        # ========== COLLECTION DROPDOWN ==========
        collection_layout = QHBoxLayout()
        collection_label = QLabel("Collection")
        collection_label.setFixedWidth(100)
        
        self.collection_combo = QComboBox()
        self._load_collections()
        
        collection_layout.addWidget(collection_label)
        collection_layout.addWidget(self.collection_combo)
        main_layout.addLayout(collection_layout)
        
        # ========== FILE DESCRIPTION ==========
        desc_label = QLabel("File Description (Optional):")
        main_layout.addWidget(desc_label)
        
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Enter file description...")
        self.description_text.setMinimumHeight(100)
        main_layout.addWidget(self.description_text)
        
        # ========== UPLOAD BUTTON ==========
        upload_btn = QPushButton("Upload File")
        upload_btn.clicked.connect(self.handle_upload)
        main_layout.addWidget(upload_btn)
        
        self.setLayout(main_layout)
    
    def _load_collections(self):
        """Load collections from data and populate dropdown"""
        from ..services.document_crud_service import DocumentCRUDService
        
        crud_service = DocumentCRUDService()
        collections = crud_service.get_all_collections()
        
        # Add "None" option
        self.collection_combo.addItem("None (Standalone)", None)
        
        # Add all collections
        for collection in collections:
            self.collection_combo.addItem(collection["name"], collection["id"])
        
        # Pre-select collection if provided
        if self.collection_id:
            for i in range(self.collection_combo.count()):
                if self.collection_combo.itemData(i) == self.collection_id:
                    self.collection_combo.setCurrentIndex(i)
                    break
    
    def handle_select_folder(self):
        """Handle folder selection button click"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder_path:
            print(f"Folder selected: {folder_path}")
            # For now, just show the folder name
            folder_name = os.path.basename(folder_path)
            self.filename_input.setText(folder_name)
    
    def handle_select_file(self):
        """Handle file selection button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx *.doc);;Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_file_path = file_path
            # Update filename input with selected file
            filename = os.path.basename(file_path)
            self.filename_input.setText(filename)
            print(f"File selected: {file_path}")

    def handle_edit_filename(self):
        """Handle edit filename action"""
        self.filename_input.setFocus()
        self.filename_input.selectAll()
    
    def handle_upload(self):
        """Handle upload button click"""
        # Validate file selection
        if not self.selected_file_path:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select a file to upload."
            )
            return
        
        filename = self.filename_input.text().strip()
        category = self.category_combo.currentText()
        collection_id = self.collection_combo.currentData()
        description = self.description_text.toPlainText()
        
        # Validate filename
        if not filename:
            QMessageBox.warning(
                self,
                "Invalid Filename",
                "Please enter a filename."
            )
            return
        
        # Import services
        from ..services.file_storage_service import FileStorageService
        from ..services.document_crud_service import DocumentCRUDService
        
        # Save file to storage
        storage_service = FileStorageService()
        save_result = storage_service.save_file(
            self.selected_file_path,
            custom_name=filename,
            category=category if category != "None" else None
        )
        
        if not save_result.get("success"):
            QMessageBox.critical(
                self,
                "Upload Failed",
                f"Failed to save file: {save_result.get('error', 'Unknown error')}"
            )
            return
        
        # Add to database
        crud_service = DocumentCRUDService()
        
        if collection_id:
            db_result = crud_service.add_file_to_collection(
                collection_id,
                save_result["filename"],
                save_result["file_path"],
                category,
                save_result["extension"],
                self.username,
                self.role
            )
        else:
            # Add as standalone file
            db_result = crud_service.add_file_standalone(
                save_result["filename"],
                save_result["file_path"],
                category,
                save_result["extension"],
                self.username,
                self.role
            )
        
        if db_result.get("success"):
            # Emit signal with file data
            self.file_uploaded.emit(db_result.get("file"))
            
            QMessageBox.information(
                self,
                "Success",
                f"File '{filename}' uploaded successfully!"
            )
            self.accept()  # Close dialog with success status
        else:
            QMessageBox.critical(
                self,
                "Upload Failed",
                f"Failed to save file data: {db_result.get('error', 'Unknown error')}"
            )
            # Clean up the physical file if database save failed
            storage_service.delete_file(save_result["file_path"])

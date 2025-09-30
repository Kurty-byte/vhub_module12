from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .Users.Admin.AdminDash import AdminDash

class DocumentsView(QWidget):
    def __init__(self, username, roles, primary_role, token):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token

        main_layout = QVBoxLayout(self)
        
        if primary_role == "admin":
            dash_widget = AdminDash(username, roles, primary_role, token)
        else:
            title_label = QLabel("Documents")
            title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            desc_label = QLabel("Hotdoggg")
            desc_label.setFont(QFont("Arial", 12))
            main_layout.addWidget(title_label)
            main_layout.addWidget(desc_label)
            main_layout.addStretch()
            
        main_layout.addWidget(dash_widget)
        self.setLayout(main_layout)

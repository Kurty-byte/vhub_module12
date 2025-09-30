from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RepositoryView(QWidget):
    def __init__(self, username, roles, primary_role, token):
        super().__init__()

        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        
        main_layout = QVBoxLayout(self)

        title_label = QLabel("Form Repository")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        desc_label = QLabel("Access and manage your forms here.")
        desc_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addStretch()

        self.setLayout(main_layout)
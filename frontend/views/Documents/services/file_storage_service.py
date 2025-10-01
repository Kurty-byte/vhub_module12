"""
File Storage Service

Handles physical file operations for the document management system.
Copies uploaded files to the FileStorage directory and manages file paths.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class FileStorageService:
    """Service for managing file storage operations"""
    
    def __init__(self, storage_directory=None):
        """
        Initialize the file storage service.
        
        Args:
            storage_directory (str): Path to storage directory. 
                                    Defaults to FileStorage in Documents folder.
        """
        if storage_directory is None:
            # Get the Documents folder path
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_directory = os.path.join(current_dir, "FileStorage")
        
        self.storage_directory = storage_directory
        self._ensure_storage_directory_exists()
    
    def _ensure_storage_directory_exists(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(self.storage_directory, exist_ok=True)
    
    def save_file(self, source_path, custom_name=None, category=None):
        """
        Copy a file to the storage directory with a unique name.
        
        Args:
            source_path (str): Path to the source file
            custom_name (str, optional): Custom name for the file
            category (str, optional): Category for organizing files
            
        Returns:
            dict: File information with keys:
                - success (bool): Whether the operation succeeded
                - file_path (str): Relative path in storage
                - filename (str): Name of the stored file
                - extension (str): File extension
                - error (str, optional): Error message if failed
        """
        try:
            # Validate source file exists
            if not os.path.exists(source_path):
                return {
                    "success": False,
                    "error": f"Source file not found: {source_path}"
                }
            
            # Get original filename and extension
            original_name = os.path.basename(source_path)
            name_without_ext, extension = os.path.splitext(original_name)
            
            # Use custom name if provided, otherwise use original
            if custom_name:
                # Remove extension from custom name if present
                custom_name_clean = os.path.splitext(custom_name)[0]
                base_name = custom_name_clean
            else:
                base_name = name_without_ext
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_name = f"{base_name}_{timestamp}{extension}"
            
            # Create category subdirectory if specified
            if category and category.lower() != "none":
                dest_directory = os.path.join(self.storage_directory, category)
                os.makedirs(dest_directory, exist_ok=True)
                dest_path = os.path.join(dest_directory, unique_name)
                relative_path = os.path.join(category, unique_name)
            else:
                dest_path = os.path.join(self.storage_directory, unique_name)
                relative_path = unique_name
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            return {
                "success": True,
                "file_path": relative_path,
                "filename": base_name,
                "extension": extension.lstrip('.'),
                "full_path": dest_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    def get_file_path(self, relative_path):
        """
        Get the full path to a stored file.
        
        Args:
            relative_path (str): Relative path in storage
            
        Returns:
            str: Full path to the file
        """
        return os.path.join(self.storage_directory, relative_path)
    
    def delete_file(self, relative_path):
        """
        Delete a file from storage.
        
        Args:
            relative_path (str): Relative path in storage
            
        Returns:
            dict: Result with success status and optional error message
        """
        try:
            full_path = self.get_file_path(relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "File not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    def file_exists(self, relative_path):
        """
        Check if a file exists in storage.
        
        Args:
            relative_path (str): Relative path in storage
            
        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = self.get_file_path(relative_path)
        return os.path.exists(full_path)

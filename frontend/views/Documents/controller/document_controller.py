"""
Document Controller

Handles all business logic for document management operations.
Role-agnostic controller that can be used by any user dashboard.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from ..Mock.data_loader import (
    get_uploaded_files, 
    get_collections, 
    get_storage_data,
    get_deleted_files,
    get_collection_by_name,
    get_mock_data_path,
    load_json_data
)
from ..services.file_storage_service import FileStorageService


class DocumentController:
    """
    Controller for document management operations.
    
    This controller handles all business logic for:
    - File CRUD operations
    - Collection management
    - Role-based filtering
    - Soft delete/restore
    - File organization
    
    Args:
        username (str): Current user's username
        roles (list): List of user roles
        primary_role (str): User's primary role
        token (str): Authentication token
    """
    
    def __init__(self, username: str, roles: List[str], primary_role: str, token: str):
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        self.file_storage = FileStorageService()
        
    # ==================== FILE OPERATIONS ====================
    
    def get_files(self, include_deleted: bool = False, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get files based on user role and filters.
        
        Args:
            include_deleted (bool): Whether to include deleted files
            filters (dict, optional): Filters to apply (category, uploader, etc.)
            
        Returns:
            list: List of file dictionaries
        """
        files = get_uploaded_files()
        
        # Filter based on role
        if self.primary_role.lower() != 'admin':
            # Non-admins only see their own files
            files = [f for f in files if f.get('uploader') == self.username]
        
        # Apply additional filters
        if filters:
            if 'category' in filters and filters['category']:
                files = [f for f in files if f.get('category') == filters['category']]
            if 'extension' in filters and filters['extension']:
                files = [f for f in files if f.get('extension') == filters['extension']]
            if 'search' in filters and filters['search']:
                search_term = filters['search'].lower()
                files = [f for f in files if search_term in f.get('filename', '').lower()]
        
        return files
    
    def get_deleted_files(self) -> List[Dict]:
        """
        Get deleted files (soft-deleted).
        
        Returns:
            list: List of deleted file dictionaries
        """
        deleted = get_deleted_files()
        
        # Filter based on role
        if self.primary_role.lower() != 'admin':
            deleted = [f for f in deleted if f.get('uploader') == self.username]
        
        return deleted
    
    def delete_file(self, filename: str, timestamp: str = None) -> Tuple[bool, str]:
        """
        Soft delete a file (move to deleted_files array).
        
        Args:
            filename (str): Name of the file to delete
            timestamp (str, optional): Timestamp to identify specific file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            files_path = get_mock_data_path('files_data.json')
            with open(files_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            uploaded_files = data.get('uploaded_files', [])
            deleted_files = data.get('deleted_files', [])
            
            # Find the file to delete
            file_to_delete = None
            for i, file_data in enumerate(uploaded_files):
                if file_data['filename'] == filename:
                    if timestamp is None or file_data.get('timestamp') == timestamp:
                        file_to_delete = uploaded_files.pop(i)
                        break
            
            if file_to_delete:
                # Add deletion metadata
                file_to_delete['deleted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_to_delete['deleted_by'] = self.username
                deleted_files.append(file_to_delete)
                
                # Save updated data
                data['uploaded_files'] = uploaded_files
                data['deleted_files'] = deleted_files
                
                with open(files_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                return True, f"File '{filename}' deleted successfully"
            else:
                return False, f"File '{filename}' not found"
                
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def restore_file(self, filename: str, deleted_at: str = None) -> Tuple[bool, str]:
        """
        Restore a soft-deleted file.
        
        Args:
            filename (str): Name of the file to restore
            deleted_at (str, optional): Deletion timestamp to identify specific file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            files_path = get_mock_data_path('files_data.json')
            with open(files_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            uploaded_files = data.get('uploaded_files', [])
            deleted_files = data.get('deleted_files', [])
            
            # Find the file to restore
            file_to_restore = None
            for i, file_data in enumerate(deleted_files):
                if file_data['filename'] == filename:
                    if deleted_at is None or file_data.get('deleted_at') == deleted_at:
                        file_to_restore = deleted_files.pop(i)
                        break
            
            if file_to_restore:
                # Remove deletion metadata
                file_to_restore.pop('deleted_at', None)
                file_to_restore.pop('deleted_by', None)
                uploaded_files.append(file_to_restore)
                
                # Save updated data
                data['uploaded_files'] = uploaded_files
                data['deleted_files'] = deleted_files
                
                with open(files_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                return True, f"File '{filename}' restored successfully"
            else:
                return False, f"File '{filename}' not found in deleted files"
                
        except Exception as e:
            return False, f"Error restoring file: {str(e)}"
    
    def permanent_delete_file(self, filename: str, deleted_at: str = None) -> Tuple[bool, str]:
        """
        Permanently delete a file from deleted_files and file system.
        
        Args:
            filename (str): Name of the file to permanently delete
            deleted_at (str, optional): Deletion timestamp to identify specific file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            files_path = get_mock_data_path('files_data.json')
            with open(files_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            deleted_files = data.get('deleted_files', [])
            
            # Find the file to permanently delete
            file_to_delete = None
            for i, file_data in enumerate(deleted_files):
                if file_data['filename'] == filename:
                    if deleted_at is None or file_data.get('deleted_at') == deleted_at:
                        file_to_delete = deleted_files.pop(i)
                        break
            
            if file_to_delete:
                # Delete physical file if exists
                file_path = file_to_delete.get('file_path')
                if file_path:
                    full_path = os.path.join(self.file_storage.storage_directory, file_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
                
                # Save updated data
                data['deleted_files'] = deleted_files
                
                with open(files_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                return True, f"File '{filename}' permanently deleted"
            else:
                return False, f"File '{filename}' not found in deleted files"
                
        except Exception as e:
            return False, f"Error permanently deleting file: {str(e)}"
    
    def upload_file(self, source_path: str, custom_name: str = None, 
                   category: str = None, description: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Upload a new file.
        
        Args:
            source_path (str): Path to the source file
            custom_name (str, optional): Custom name for the file
            category (str, optional): Category for the file
            description (str, optional): File description
            
        Returns:
            tuple: (success: bool, message: str, file_data: dict or None)
        """
        try:
            # Save file using storage service
            result = self.file_storage.save_file(source_path, custom_name, category)
            
            if not result['success']:
                return False, result.get('error', 'Upload failed'), None
            
            # Create file metadata
            file_data = {
                'filename': result['filename'],
                'time': datetime.now().strftime("%I:%M %p").lower(),
                'extension': result['extension'],
                'file_path': result['file_path'],
                'category': category or 'None',
                'uploaded_date': datetime.now().strftime("%m/%d/%Y"),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'uploader': self.username,
                'role': self.primary_role
            }
            
            if description:
                file_data['description'] = description
            
            # Add to JSON data
            files_path = get_mock_data_path('files_data.json')
            with open(files_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            uploaded_files = data.get('uploaded_files', [])
            uploaded_files.append(file_data)
            data['uploaded_files'] = uploaded_files
            
            with open(files_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True, "File uploaded successfully", file_data
            
        except Exception as e:
            return False, f"Error uploading file: {str(e)}", None
    
    # ==================== COLLECTION OPERATIONS ====================
    
    def get_collections(self) -> List[Dict]:
        """
        Get collections based on user role.
        
        Returns:
            list: List of collection dictionaries
        """
        collections = get_collections()
        
        # For now, all users see all collections
        # Can add role-based filtering later
        return collections
    
    def create_collection(self, name: str, icon: str = 'folder.png') -> Tuple[bool, str, Optional[Dict]]:
        """
        Create a new collection.
        
        Args:
            name (str): Collection name
            icon (str): Icon filename
            
        Returns:
            tuple: (success: bool, message: str, collection_data: dict or None)
        """
        try:
            collections_path = get_mock_data_path('collections_data.json')
            with open(collections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collections = data.get('collections', [])
            
            # Check if collection already exists
            if any(c['name'].lower() == name.lower() for c in collections):
                return False, f"Collection '{name}' already exists", None
            
            # Create new collection
            new_id = max([c['id'] for c in collections], default=0) + 1
            collection_data = {
                'id': new_id,
                'name': name,
                'icon': icon,
                'files': [],
                'created_by': self.username,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            collections.append(collection_data)
            data['collections'] = collections
            
            with open(collections_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True, f"Collection '{name}' created successfully", collection_data
            
        except Exception as e:
            return False, f"Error creating collection: {str(e)}", None
    
    def delete_collection(self, collection_name: str) -> Tuple[bool, str]:
        """
        Delete a collection (and optionally its files).
        
        Args:
            collection_name (str): Name of the collection to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collections_path = get_mock_data_path('collections_data.json')
            with open(collections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collections = data.get('collections', [])
            
            # Find and remove the collection
            collection_found = False
            for i, collection in enumerate(collections):
                if collection['name'].lower() == collection_name.lower():
                    collections.pop(i)
                    collection_found = True
                    break
            
            if collection_found:
                data['collections'] = collections
                
                with open(collections_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                return True, f"Collection '{collection_name}' deleted successfully"
            else:
                return False, f"Collection '{collection_name}' not found"
                
        except Exception as e:
            return False, f"Error deleting collection: {str(e)}"
    
    def add_file_to_collection(self, collection_name: str, file_data: Dict) -> Tuple[bool, str]:
        """
        Add a file to a collection.
        
        Args:
            collection_name (str): Name of the collection
            file_data (dict): File data to add
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collections_path = get_mock_data_path('collections_data.json')
            with open(collections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collections = data.get('collections', [])
            
            # Find the collection
            for collection in collections:
                if collection['name'].lower() == collection_name.lower():
                    collection['files'].append(file_data)
                    
                    with open(collections_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    
                    return True, f"File added to collection '{collection_name}'"
            
            return False, f"Collection '{collection_name}' not found"
            
        except Exception as e:
            return False, f"Error adding file to collection: {str(e)}"
    
    def remove_file_from_collection(self, collection_name: str, filename: str) -> Tuple[bool, str]:
        """
        Remove a file from a collection.
        
        Args:
            collection_name (str): Name of the collection
            filename (str): Name of the file to remove
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collections_path = get_mock_data_path('collections_data.json')
            with open(collections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collections = data.get('collections', [])
            
            # Find the collection
            for collection in collections:
                if collection['name'].lower() == collection_name.lower():
                    files = collection.get('files', [])
                    
                    # Remove the file
                    for i, file_data in enumerate(files):
                        if file_data['filename'] == filename:
                            files.pop(i)
                            
                            with open(collections_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2)
                            
                            return True, f"File removed from collection '{collection_name}'"
                    
                    return False, f"File '{filename}' not found in collection"
            
            return False, f"Collection '{collection_name}' not found"
            
        except Exception as e:
            return False, f"Error removing file from collection: {str(e)}"
    
    # ==================== UTILITY METHODS ====================
    
    def get_file_details(self, filename: str, timestamp: str = None) -> Optional[Dict]:
        """
        Get detailed information about a file.
        
        Args:
            filename (str): Name of the file
            timestamp (str, optional): Timestamp to identify specific file
            
        Returns:
            dict or None: File details if found
        """
        files = get_uploaded_files()
        
        for file_data in files:
            if file_data['filename'] == filename:
                if timestamp is None or file_data.get('timestamp') == timestamp:
                    return file_data
        
        return None
    
    def get_storage_info(self) -> Dict:
        """
        Get storage usage information.
        
        Returns:
            dict: Storage information
        """
        return get_storage_data()
    
    def can_edit_file(self, file_data: Dict) -> bool:
        """
        Check if current user can edit a file.
        
        Args:
            file_data (dict): File data to check
            
        Returns:
            bool: True if user can edit
        """
        if self.primary_role.lower() == 'admin':
            return True
        
        return file_data.get('uploader') == self.username
    
    def can_delete_file(self, file_data: Dict) -> bool:
        """
        Check if current user can delete a file.
        
        Args:
            file_data (dict): File data to check
            
        Returns:
            bool: True if user can delete
        """
        if self.primary_role.lower() == 'admin':
            return True
        
        return file_data.get('uploader') == self.username

"""
Document CRUD Service

Handles Create, Read, Update, Delete operations for documents and collections.
Manages data persistence to JSON files.
"""

import json
import os
from datetime import datetime


class DocumentCRUDService:
    """Service for managing document and collection data"""
    
    def __init__(self):
        """Initialize the CRUD service with paths to data files"""
        self.mock_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "Mock"
        )
        self.collections_file = os.path.join(self.mock_dir, "collections_data.json")
        self.files_file = os.path.join(self.mock_dir, "files_data.json")
    
    def _load_json(self, filepath):
        """Load JSON data from file with robust error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Handle empty file
                if not content:
                    print(f"Warning: Empty file '{filepath}', returning default structure")
                    return self._get_default_structure(filepath)
                data = json.loads(content)
                # Handle completely empty JSON objects
                if not data:
                    return self._get_default_structure(filepath)
                return data
        except FileNotFoundError:
            print(f"Warning: File not found '{filepath}', creating default structure")
            return self._get_default_structure(filepath)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in '{filepath}': {e}, returning default structure")
            return self._get_default_structure(filepath)
    
    def _get_default_structure(self, filepath):
        """Get default structure based on file type"""
        if 'collections' in filepath:
            return {"collections": []}
        elif 'files' in filepath:
            return {"uploaded_files": [], "deleted_files": []}
        else:
            return {}
    
    def _save_json(self, filepath, data):
        """Save data to JSON file with error handling"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON to '{filepath}': {e}")
            return False
    
    # ========== COLLECTION OPERATIONS ==========
    
    def create_collection(self, name, icon="folder.png"):
        """
        Create a new collection.
        
        Args:
            name (str): Collection name
            icon (str): Icon filename
            
        Returns:
            dict: Result with success status and collection data
        """
        data = self._load_json(self.collections_file)
        collections = data.get("collections", [])
        
        # Generate new ID
        new_id = max([c.get("id", 0) for c in collections], default=0) + 1
        
        # Create new collection
        new_collection = {
            "id": new_id,
            "name": name,
            "icon": icon,
            "files": []
        }
        
        collections.append(new_collection)
        data["collections"] = collections
        
        if self._save_json(self.collections_file, data):
            return {
                "success": True,
                "collection": new_collection
            }
        else:
            return {
                "success": False,
                "error": "Failed to save collection"
            }
    
    def get_all_collections(self):
        """Get all collections with safe fallback"""
        data = self._load_json(self.collections_file)
        collections = data.get("collections", [])
        # Ensure it's a list
        if not isinstance(collections, list):
            print(f"Warning: collections is not a list, returning empty list")
            return []
        return collections
    
    def get_collection_by_id(self, collection_id):
        """Get a collection by ID"""
        collections = self.get_all_collections()
        for collection in collections:
            if collection.get("id") == collection_id:
                return collection
        return None
    
    def get_collection_by_name(self, name):
        """Get a collection by name"""
        collections = self.get_all_collections()
        for collection in collections:
            if collection.get("name") == name:
                return collection
        return None
    
    # ========== FILE OPERATIONS ==========
    
    def add_file_to_collection(self, collection_id, filename, file_path, category, extension, uploader, role):
        """
        Add a file to a specific collection.
        
        Args:
            collection_id (int): ID of the collection
            filename (str): Name of the file
            file_path (str): Path to the file in storage
            category (str): File category
            extension (str): File extension
            uploader (str): Username of the uploader
            role (str): Role of the uploader (can include subroles with '-')
            
        Returns:
            dict: Result with success status
        """
        data = self._load_json(self.collections_file)
        collections = data.get("collections", [])
        
        # Find the collection
        collection_found = False
        for collection in collections:
            if collection.get("id") == collection_id:
                collection_found = True
                
                # Add file to collection
                now = datetime.now()
                new_file = {
                    "filename": filename,
                    "time": now.strftime("%I:%M %p").lower(),
                    "extension": extension,
                    "file_path": file_path,
                    "category": category,
                    "uploaded_date": now.strftime("%m/%d/%Y"),
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "uploader": uploader,
                    "role": role
                }
                
                collection["files"].append(new_file)
                break
        
        if not collection_found:
            return {
                "success": False,
                "error": "Collection not found"
            }
        
        # Save updated collections
        data["collections"] = collections
        if self._save_json(self.collections_file, data):
            # Also add to uploaded files list
            self._add_to_uploaded_files(filename, file_path, category, extension, uploader, role)
            return {
                "success": True,
                "file": new_file
            }
        else:
            return {
                "success": False,
                "error": "Failed to save file"
            }
    
    def add_file_standalone(self, filename, file_path, category, extension, uploader, role):
        """
        Add a file to the uploaded files list (not in a collection).
        
        Args:
            filename (str): Name of the file
            file_path (str): Path to the file in storage
            category (str): File category
            extension (str): File extension
            uploader (str): Username of the uploader
            role (str): Role of the uploader (can include subroles with '-')
        """
        now = datetime.now()
        new_file = {
            "filename": filename,
            "time": now.strftime("%I:%M %p").lower(),
            "extension": extension,
            "file_path": file_path,
            "category": category,
            "uploaded_date": now.strftime("%m/%d/%Y"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "uploader": uploader,
            "role": role
        }
        
        if self._add_to_uploaded_files(filename, file_path, category, extension, uploader, role):
            return {
                "success": True,
                "file": new_file
            }
        else:
            return {
                "success": False,
                "error": "Failed to save file"
            }
    
    def _add_to_uploaded_files(self, filename, file_path, category, extension, uploader, role):
        """Add a file to the uploaded files list"""
        data = self._load_json(self.files_file)
        uploaded_files = data.get("uploaded_files", [])
        
        now = datetime.now()
        new_file = {
            "filename": filename,
            "time": now.strftime("%I:%M %p").lower(),
            "extension": extension,
            "file_path": file_path,
            "category": category,
            "uploaded_date": now.strftime("%m/%d/%Y"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "uploader": uploader,
            "role": role
        }
        
        uploaded_files.append(new_file)
        data["uploaded_files"] = uploaded_files
        
        return self._save_json(self.files_file, data)
    
    def get_all_uploaded_files(self):
        """Get all uploaded files with safe fallback"""
        data = self._load_json(self.files_file)
        uploaded_files = data.get("uploaded_files", [])
        # Ensure it's a list
        if not isinstance(uploaded_files, list):
            print(f"Warning: uploaded_files is not a list, returning empty list")
            return []
        return uploaded_files
    
    def get_files_by_collection(self, collection_id):
        """Get all files in a specific collection"""
        collection = self.get_collection_by_id(collection_id)
        if collection:
            return collection.get("files", [])
        return []

# Mock Data for Document Management System

This folder contains mock data files used by the Document Management interface for development and testing purposes.

## ⚠️ Important Note

The actual data files (`*.json`) are **NOT tracked by git** to prevent committing user-generated test data. 

**Don't worry!** The application automatically creates these files with proper default structures on first run if they don't exist. Thanks to the robust error handling in `data_loader.py`, missing files are handled gracefully.

## Files

### 1. `files_data.json`
Contains mock data for uploaded files and deleted files.

**Structure:**
```json
{
  "uploaded_files": [
    {
      "filename": "string",
      "time": "string",
      "extension": "string"
    }
  ],
  "deleted_files": [
    {
      "filename": "string",
      "time": "string",
      "extension": "string"
    }
  ]
}
```

### 2. `collections_data.json`
Contains mock data for document collections and their associated files.

**Structure:**
```json
{
  "collections": [
    {
      "id": number,
      "name": "string",
      "icon": "string (emoji)",
      "files": [
        {
          "filename": "string",
          "time": "string",
          "extension": "string"
        }
      ]
    }
  ]
}
```

### 3. `storage_data.json`
Contains mock data for storage usage statistics.

**Structure:**
```json
{
  "total_size_gb": number,
  "used_size_gb": number,
  "free_size_gb": number,
  "usage_percentage": number
}
```

## Usage

The `data_loader.py` module provides convenient functions to load this data:

```python
from Mock.data_loader import (
    get_uploaded_files,
    get_deleted_files,
    get_collections,
    get_collection_by_name,
    get_storage_data,
    get_all_mock_data
)

# Load uploaded files
files = get_uploaded_files()

# Load a specific collection
collection = get_collection_by_name("Collection 1")

# Load storage data
storage = get_storage_data()
```

## Modifying Mock Data

To add or modify test data:

1. Open the appropriate JSON file
2. Follow the existing structure
3. Save the file
4. The changes will be reflected immediately when the application loads the data

**Note:** Ensure JSON syntax is valid. Use a JSON validator if needed.

## Benefits of JSON-based Mock Data

- **Easy to modify**: Update test data without changing code
- **Realistic**: Mimics data fetched from an API
- **Reusable**: Same data can be used across different views
- **Version control friendly**: Changes are tracked separately from code
- **Scalable**: Easy to add more data as needed

## Future Migration

When migrating to a real backend API:

1. Update the functions in `data_loader.py` to make API calls
2. Keep the same function signatures
3. No changes needed in the view files
4. The JSON files can remain as fallback data for offline mode

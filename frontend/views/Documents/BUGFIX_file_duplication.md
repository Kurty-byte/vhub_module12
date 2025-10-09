# File Duplication Bug Fix

## Problem
After uploading a file and relaunching the application, the file appears duplicated in the uploaded files list in AdminDash.

## Root Cause
The `_add_to_files_list()` method in `DocumentCRUDService` was appending files to the files array without checking if a file with the same `file_id` already existed. This could lead to duplicates if:

1. The method was called multiple times with the same `file_id`
2. There was a race condition during concurrent saves
3. The upload signal chain triggered multiple save operations

## Solution Applied

Added duplicate prevention check in `_add_to_files_list()`:

```python
# CRITICAL FIX: Check if file_id already exists (prevent duplicates)
existing_file = next((f for f in all_files if f.get('file_id') == file_id), None)
if existing_file:
    print(f"WARNING: File with file_id {file_id} already exists in files array. Skipping duplicate insertion.")
    return True  # Return success but don't add duplicate
```

This ensures that:
- Each `file_id` only appears once in the files array
- Duplicate insertion attempts are caught and logged
- The method returns success to avoid breaking the upload flow

## Testing Steps

1. Delete all files from the system
2. Upload a new file to a collection
3. Verify it appears once in the uploaded files list
4. Close and relaunch the application
5. Verify the file still appears only once (no duplicates)
6. Upload another file
7. Repeat relaunch test

## Additional Investigation Needed

If duplicates still occur after this fix, check:

1. **File upload dialog signal chain** - ensure `file_uploaded.emit()` is only called once per upload
2. **Controller vs CRUD service** - verify only ONE path is used per upload:
   - Collection uploads → `DocumentCRUDService.add_file_to_collection()`
   - Standalone uploads → `DocumentController.upload_file()`
3. **JSON save race conditions** - ensure no concurrent writes to `files_data.json`
4. **File ID counter** - verify `next_file_id` is properly incremented and saved

## Files Modified
- `frontend/views/Documents/services/document_crud_service.py` - Added duplicate check in `_add_to_files_list()`

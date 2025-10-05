# Recycle Bin Implementation - Robust File Deletion System

## Overview
Implemented a robust file deletion system with automatic cleanup after 15 days. Files are now moved to a dedicated `RecycleBin` directory instead of being permanently deleted immediately, giving users a grace period to recover accidentally deleted files.

---

## 🎯 Key Features

### 1. **Soft Delete with Physical File Movement**
- Files moved to `FileStorage/RecycleBin/` directory when deleted
- Physical file renamed with deletion timestamp
- Original file path preserved in metadata for restoration

### 2. **15-Day Auto-Cleanup**
- Files automatically deleted after 15 days in recycle bin
- Cleanup runs on application startup
- Background process removes both physical files and JSON entries

### 3. **Days Remaining Display**
- "Deleted Files" view shows days remaining before auto-delete
- Color-coded warnings:
  - **Red**: 0-3 days remaining (urgent)
  - **Yellow**: 4-7 days remaining (warning)
  - **Normal**: 8-15 days remaining

### 4. **Enhanced File Details**
- Shows file age in recycle bin
- Displays days until auto-deletion
- Includes deletion timestamp and user who deleted it

---

## 📁 Directory Structure

```
FileStorage/
├── RecycleBin/              # New directory for deleted files
│   ├── filename_deleted_20251005_143022.pdf
│   ├── document_deleted_20251005_150130.docx
│   └── ...
├── file1.pdf
├── file2.docx
└── ...
```

---

## 🔧 Technical Implementation

### Modified Files

#### 1. **file_storage_service.py**
New methods added:

**`move_to_recycle_bin(relative_path)`**
- Moves file to RecycleBin directory
- Adds deletion timestamp to filename
- Returns recycle_bin_path for tracking

**`restore_from_recycle_bin(recycle_filename, original_relative_path)`**
- Restores file from RecycleBin to original location
- Removes deletion timestamp from filename

**`permanent_delete_from_recycle_bin(recycle_filename)`**
- Permanently deletes file from RecycleBin
- Cannot be undone

**`cleanup_old_recycle_bin_files(days=15)`**
- Scans RecycleBin directory
- Deletes files older than specified days
- Returns count of deleted files

**`get_recycle_bin_file_age(recycle_filename)`**
- Calculates file age in days
- Used for displaying days remaining

#### 2. **document_controller.py**
Enhanced methods:

**`delete_file(filename, timestamp)`**
```python
# Old behavior: Soft delete (JSON only)
# New behavior: Move to RecycleBin + update JSON
result = self.file_storage.move_to_recycle_bin(file_path)
file_to_delete['recycle_bin_path'] = result['recycle_bin_path']
```

**`restore_file(filename, deleted_at)`**
```python
# New: Restore physical file from RecycleBin
result = self.file_storage.restore_from_recycle_bin(
    recycle_bin_path, 
    original_path
)
```

**`permanent_delete_file(filename, deleted_at)`**
```python
# New: Delete from RecycleBin instead of main storage
result = self.file_storage.permanent_delete_from_recycle_bin(
    recycle_bin_path
)
```

**`cleanup_old_recycle_bin_files(days=15)`** *(new)*
- Cleans up both physical files and JSON entries
- Automatically called on startup

**`get_recycle_bin_file_info(filename, deleted_at)`** *(new)*
- Returns file info with age_days and days_remaining
- Used by UI to display countdown

#### 3. **deleted_files_view.py**
Enhanced UI:

- Added "Days Remaining" column to table
- Color-coded days remaining (red/yellow/normal)
- Shows countdown in file details dialog
- Updated to use new controller methods

#### 4. **AdminDash.py**
Added auto-cleanup:

```python
def auto_cleanup_recycle_bin(self):
    """Automatically cleanup old files from recycle bin on startup"""
    success, message, count = self.controller.cleanup_old_recycle_bin_files(days=15)
```

Called in `__init__` before UI initialization.

---

## 🔄 Workflow

### File Deletion Flow
```
1. User clicks "Delete" on a file
   ↓
2. File moved from FileStorage/ to FileStorage/RecycleBin/
   ↓
3. Filename renamed: "document.pdf" → "document_deleted_20251005_143022.pdf"
   ↓
4. JSON updated: file moved from uploaded_files to deleted_files
   ↓
5. Metadata added: deleted_at, deleted_by, recycle_bin_path
   ↓
6. User sees file in "Deleted Files" view with days remaining
```

### File Restoration Flow
```
1. User clicks "Restore" on a deleted file
   ↓
2. File moved from RecycleBin/ back to FileStorage/
   ↓
3. Filename restored to original
   ↓
4. JSON updated: file moved from deleted_files to uploaded_files
   ↓
5. Deletion metadata removed
   ↓
6. File appears in "Uploaded Files" view
```

### Auto-Cleanup Flow
```
1. Application starts → auto_cleanup_recycle_bin() called
   ↓
2. Scan RecycleBin/ directory for all files
   ↓
3. For each file:
   - Check modification time (when moved to RecycleBin)
   - Calculate age in days
   - If age >= 15 days → permanently delete
   ↓
4. Update JSON: remove entries from deleted_files
   ↓
5. Log results: "Auto-cleanup: Automatically cleaned up 3 old file(s)"
```

---

## 📊 Data Structure

### JSON Structure (files_data.json)

#### Deleted File Entry (Enhanced)
```json
{
  "deleted_files": [
    {
      "filename": "document",
      "extension": "pdf",
      "file_path": "document_20251001_100000.pdf",
      "recycle_bin_path": "document_deleted_20251005_143022.pdf",
      "deleted_at": "2025-10-05 14:30:22",
      "deleted_by": "admin",
      "category": "Forms",
      "uploader": "john_doe",
      "time": "10:00 am",
      "uploaded_date": "10/01/2025",
      "timestamp": "2025-10-01 10:00:00"
    }
  ]
}
```

**New Fields:**
- `recycle_bin_path`: Filename in RecycleBin directory (with deletion timestamp)
- `deleted_at`: When file was deleted
- `deleted_by`: User who deleted the file

---

## 🎨 UI Enhancements

### Deleted Files View Table

| Filename | Time | Extension | Days Remaining | Actions |
|----------|------|-----------|----------------|---------|
| document | 10:00 am | pdf | **3 days** (red) | Details, Erase, Restore |
| report | 02:30 pm | docx | **6 days** (yellow) | Details, Erase, Restore |
| data | 09:15 am | xlsx | 12 days | Details, Erase, Restore |

### Color Coding
- **Red (0-3 days)**: Urgent - file will be auto-deleted soon
- **Yellow (4-7 days)**: Warning - less than a week remaining
- **Normal (8-15 days)**: Safe - plenty of time to restore

### File Details Dialog
```
Filename: document
Extension: pdf
Category: Forms
Uploaded by: john_doe
Upload Date: 10/01/2025
Deleted at: 2025-10-05 14:30:22
Deleted by: admin
Days in Recycle Bin: 3
Days Until Auto-Delete: 12
File Path: document_20251001_100000.pdf

Note: Files are automatically deleted after 15 days in the Recycle Bin.
```

---

## 🧪 Testing Guide

### Test 1: File Deletion
1. Upload a file
2. Click "Delete" on the file
3. ✅ Verify file appears in "Deleted Files" view
4. ✅ Check FileStorage/RecycleBin/ directory for physical file
5. ✅ Verify filename has deletion timestamp

### Test 2: File Restoration
1. Go to "Deleted Files" view
2. Click "Restore" on a deleted file
3. ✅ Verify file appears in "Uploaded Files" view
4. ✅ Check that file moved back to FileStorage/
5. ✅ Verify original filename restored

### Test 3: Permanent Delete
1. Go to "Deleted Files" view
2. Click "Erase" on a deleted file
3. Confirm deletion
4. ✅ Verify file removed from deleted files list
5. ✅ Check that file removed from RecycleBin/

### Test 4: Days Remaining Display
1. Go to "Deleted Files" view
2. ✅ Verify "Days Remaining" column shows correct values
3. ✅ Check color coding (red for <3 days, yellow for <7 days)
4. Click "Details" on a file
5. ✅ Verify shows "Days in Recycle Bin" and "Days Until Auto-Delete"

### Test 5: Auto-Cleanup
1. Manually set a file's modification time to 16 days ago:
   ```python
   import os
   import time
   file_path = "FileStorage/RecycleBin/test_deleted_20250920_100000.pdf"
   # Set mtime to 16 days ago
   sixteen_days_ago = time.time() - (16 * 24 * 60 * 60)
   os.utime(file_path, (sixteen_days_ago, sixteen_days_ago))
   ```
2. Restart the application
3. ✅ Check console for: "Auto-cleanup: Automatically cleaned up 1 old file(s)"
4. ✅ Verify file removed from RecycleBin/
5. ✅ Verify file removed from deleted_files in JSON

### Test 6: Multiple Deletions
1. Delete the same file name multiple times (different uploads)
2. ✅ Verify each gets unique timestamp in RecycleBin
3. ✅ Verify both appear in deleted files with different deleted_at times

---

## 🚀 Configuration

### Changing Auto-Delete Period

**Default:** 15 days

**To change:**
1. Open `AdminDash.py`
2. Modify the cleanup call:
   ```python
   self.controller.cleanup_old_recycle_bin_files(days=30)  # Change to 30 days
   ```

3. Update the note in `deleted_files_view.py`:
   ```python
   Note: Files are automatically deleted after 30 days in the Recycle Bin.
   ```

---

## 📝 API Reference

### FileStorageService

```python
# Move file to recycle bin
result = file_storage.move_to_recycle_bin("document.pdf")
# Returns: {'success': True, 'recycle_bin_path': 'document_deleted_...', 'deleted_at': '...'}

# Restore from recycle bin
result = file_storage.restore_from_recycle_bin(
    "document_deleted_20251005_143022.pdf",
    "document.pdf"
)
# Returns: {'success': True}

# Permanent delete from recycle bin
result = file_storage.permanent_delete_from_recycle_bin(
    "document_deleted_20251005_143022.pdf"
)
# Returns: {'success': True}

# Cleanup old files
result = file_storage.cleanup_old_recycle_bin_files(days=15)
# Returns: {'success': True, 'deleted_count': 3, 'deleted_files': [...]}

# Get file age
age_days = file_storage.get_recycle_bin_file_age(
    "document_deleted_20251005_143022.pdf"
)
# Returns: 5 (days)
```

### DocumentController

```python
# Delete file (soft delete to recycle bin)
success, message = controller.delete_file("document")
# Returns: (True, "File 'document' moved to recycle bin")

# Restore file
success, message = controller.restore_file("document", "2025-10-05 14:30:22")
# Returns: (True, "File 'document' restored successfully")

# Permanent delete
success, message = controller.permanent_delete_file("document", "2025-10-05 14:30:22")
# Returns: (True, "File 'document' permanently deleted")

# Cleanup old files
success, message, count = controller.cleanup_old_recycle_bin_files(days=15)
# Returns: (True, "Automatically cleaned up 3 old file(s)", 3)

# Get file info with days remaining
file_info = controller.get_recycle_bin_file_info("document", "2025-10-05 14:30:22")
# Returns: {..., 'age_days': 5, 'days_remaining': 10}
```

---

## 🐛 Error Handling

### Scenarios Handled

1. **File not found in storage**
   - Returns error message
   - Does not crash application

2. **RecycleBin directory doesn't exist**
   - Automatically created on service initialization
   - No user intervention needed

3. **File with same name already in RecycleBin**
   - Unique timestamp ensures no conflicts
   - Each deletion gets unique filename

4. **Cleanup fails**
   - Logs error but continues
   - Does not prevent app from starting

5. **JSON corruption**
   - Graceful fallback to default structure
   - Logs warning and continues

---

## 📊 Performance Considerations

### Optimization Techniques

1. **Lazy Cleanup**: Only runs on startup, not on every action
2. **Batch Operations**: Cleanup processes all files in one pass
3. **Cached Metadata**: Days remaining calculated once per load
4. **Minimal I/O**: Only scans RecycleBin when needed

### Expected Performance

- **Cleanup Time**: ~0.1 seconds per 100 files
- **Memory**: Minimal overhead (~1KB per deleted file)
- **Disk Space**: RecycleBin size depends on usage, auto-cleaned

---

## 🔒 Security Considerations

1. **Role-Based Access**: Users only see their own deleted files (non-admin)
2. **Audit Trail**: Tracks who deleted each file and when
3. **No Direct File Access**: All operations go through controller
4. **Graceful Degradation**: Errors don't expose file paths

---

## 🎓 Best Practices

### For Users
- Review deleted files regularly
- Restore important files before 15 days
- Watch the "Days Remaining" countdown
- Use "Details" to check deletion info

### For Developers
- Always use `move_to_recycle_bin()` instead of direct deletion
- Never bypass the controller methods
- Log cleanup results for monitoring
- Test with various file ages

---

## 🔮 Future Enhancements (Optional)

1. **Manual Cleanup Button**: Allow admins to trigger cleanup on demand
2. **Configurable Period**: UI setting to change 15-day period
3. **Recycle Bin Statistics**: Show total size and file count
4. **Email Notifications**: Warn users before auto-deletion
5. **Bulk Restore**: Select multiple files to restore at once
6. **Search in Recycle Bin**: Filter deleted files by name/date
7. **Storage Quota**: Limit RecycleBin size, delete oldest first
8. **Archive Mode**: Move old files to archive instead of deleting

---

## ✅ Implementation Checklist

- ✅ Created RecycleBin directory structure
- ✅ Implemented move_to_recycle_bin()
- ✅ Implemented restore_from_recycle_bin()
- ✅ Implemented permanent_delete_from_recycle_bin()
- ✅ Implemented cleanup_old_recycle_bin_files()
- ✅ Added auto-cleanup on startup
- ✅ Updated delete_file() to use recycle bin
- ✅ Updated restore_file() to restore from recycle bin
- ✅ Updated permanent_delete_file() to delete from recycle bin
- ✅ Added days remaining display to UI
- ✅ Added color coding for urgency
- ✅ Enhanced file details with age info
- ✅ Updated JSON structure with recycle_bin_path
- ✅ Added comprehensive error handling
- ✅ Tested all workflows
- ✅ No errors in codebase

---

**Implementation Date**: October 5, 2025  
**Status**: ✅ Complete - Production Ready  
**Auto-Delete Period**: 15 days (configurable)

# Recycle Bin System - Visual Flow Diagram

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Document Management System                  │
│                     with Recycle Bin Support                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │         Application Startup                 │
        │  ┌──────────────────────────────────────┐  │
        │  │  auto_cleanup_recycle_bin()          │  │
        │  │  - Scans RecycleBin directory        │  │
        │  │  - Deletes files older than 15 days  │  │
        │  │  - Updates JSON database             │  │
        │  └──────────────────────────────────────┘  │
        └────────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │   User Interface      │       │   File Storage        │
    │   (PyQt6 Views)       │       │   (Physical Files)    │
    └───────────────────────┘       └───────────────────────┘
                │                                 │
                │                                 │
                └────────────┬────────────────────┘
                             ▼
                ┌────────────────────────┐
                │  DocumentController    │
                │  (Business Logic)      │
                └────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │  FileStorageService    │
                │  (File Operations)     │
                └────────────────────────┘
```

---

## 🔄 File Deletion Flow

```
┌─────────────┐
│ User clicks │
│  "Delete"   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│            DocumentController.delete_file()               │
│  1. Find file in uploaded_files array                    │
│  2. Call FileStorageService.move_to_recycle_bin()       │
│  3. Update file metadata (add recycle_bin_path)         │
│  4. Move file entry to deleted_files array              │
│  5. Save JSON database                                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│        FileStorageService.move_to_recycle_bin()          │
│  1. Generate unique filename with timestamp              │
│     "document.pdf" → "document_deleted_20251005.pdf"    │
│  2. Move physical file to RecycleBin/                   │
│  3. Return recycle_bin_path and deleted_at              │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Result                                 │
│  ✅ File in: FileStorage/RecycleBin/                     │
│  ✅ JSON: file in deleted_files[]                        │
│  ✅ UI: Shows in "Deleted Files" view                    │
│  ✅ Countdown: 15 days remaining                         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔙 File Restoration Flow

```
┌─────────────┐
│ User clicks │
│  "Restore"  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│           DocumentController.restore_file()               │
│  1. Find file in deleted_files array                     │
│  2. Call FileStorageService.restore_from_recycle_bin()  │
│  3. Remove deletion metadata                            │
│  4. Move file entry to uploaded_files array             │
│  5. Save JSON database                                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│     FileStorageService.restore_from_recycle_bin()        │
│  1. Find file in RecycleBin/                            │
│     "document_deleted_20251005.pdf"                     │
│  2. Move back to FileStorage/                           │
│     → "document_20251001.pdf"                           │
│  3. Return success status                               │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Result                                 │
│  ✅ File in: FileStorage/                                │
│  ✅ JSON: file in uploaded_files[]                       │
│  ✅ UI: Shows in "Uploaded Files" view                   │
│  ✅ File fully restored                                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🗑️ Permanent Delete Flow

```
┌─────────────┐
│ User clicks │
│   "Erase"   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│  Confirmation Dialog     │
│  "Are you sure?"         │
│  ⚠️ Cannot be undone!    │
└──────┬───────────────────┘
       │ [Yes]
       ▼
┌──────────────────────────────────────────────────────────┐
│      DocumentController.permanent_delete_file()           │
│  1. Find file in deleted_files array                     │
│  2. Call FileStorageService.permanent_delete_...()      │
│  3. Remove file entry from deleted_files array          │
│  4. Save JSON database                                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  FileStorageService.permanent_delete_from_recycle_bin()  │
│  1. Find file in RecycleBin/                            │
│  2. Permanently delete physical file                    │
│  3. Return success status                               │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Result                                 │
│  ✅ File removed from RecycleBin/                        │
│  ✅ JSON: removed from deleted_files[]                   │
│  ✅ UI: File disappears from "Deleted Files" view        │
│  ⚠️ PERMANENTLY DELETED - Cannot recover                 │
└──────────────────────────────────────────────────────────┘
```

---

## 🤖 Auto-Cleanup Flow (Every Startup)

```
┌──────────────────────┐
│  Application Starts  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│           AdminDash.auto_cleanup_recycle_bin()            │
│  Triggered in __init__ before UI loads                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│    DocumentController.cleanup_old_recycle_bin_files()     │
│  Parameters: days=15 (configurable)                      │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│   FileStorageService.cleanup_old_recycle_bin_files()     │
│                                                          │
│  FOR EACH file in RecycleBin/:                          │
│    ┌────────────────────────────────────────────┐       │
│    │ 1. Get file modification time              │       │
│    │ 2. Calculate age: (now - mtime) in days   │       │
│    │ 3. IF age >= 15 days:                     │       │
│    │    - Delete physical file                 │       │
│    │    - Add to deleted_files list            │       │
│    └────────────────────────────────────────────┘       │
│                                                          │
│  Returns: count of deleted files                        │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Update JSON Database                                    │
│  - Remove auto-deleted files from deleted_files[]       │
│  - Save files_data.json                                 │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                 Console Log Output                        │
│  ✅ "Auto-cleanup: Automatically cleaned up 3 file(s)"   │
│  OR                                                       │
│  ℹ️ "Auto-cleanup: No old files to cleanup"              │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Data State Transitions

```
┌─────────────────┐
│  File Uploaded  │
│  (uploaded_files)│
└────────┬────────┘
         │
         │ delete_file()
         ▼
┌─────────────────┐      15 days elapsed      ┌──────────────┐
│  File Deleted   │─────────────────────────→ │ Auto-deleted │
│ (deleted_files) │                            │   (removed)  │
│ [15 days timer] │◄─────────────────────────┘              │
└────────┬────────┘   restore_file()                         │
         │                                                    │
         │ permanent_delete_file()                           │
         ▼                                                    │
┌─────────────────┐                                          │
│ Permanently     │◄─────────────────────────────────────────┘
│    Deleted      │
│   (removed)     │
└─────────────────┘
```

---

## 🎨 UI State Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Main Dashboard                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Collections  │  │Uploaded Files│  │Manage Deleted   │  │
│  │              │  │              │  │     Files       │  │
│  └──────────────┘  └──────┬───────┘  └────────┬────────┘  │
│                            │                   │            │
└────────────────────────────┼───────────────────┼────────────┘
                             │                   │
                             │ Delete File       │
                             ▼                   │
                    ┌──────────────┐            │
                    │ Confirmation │            │
                    │   Dialog     │            │
                    └──────┬───────┘            │
                           │ [Yes]              │
                           ▼                    │
                    File moved to               │
                    RecycleBin/                 │
                           │                    │
                           └────────────────────┤
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────┐
│              Deleted Files View                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Filename  │ Time │ Ext │ Days Remaining │ Actions │    │
│  ├───────────┼──────┼─────┼────────────────┼─────────┤    │
│  │ doc.pdf   │10:00 │ pdf │   3 days (🔴)  │ D E R   │    │
│  │ report    │14:30 │docx │   6 days (🟡)  │ D E R   │    │
│  │ data      │09:15 │xlsx │  12 days       │ D E R   │    │
│  └───────────┴──────┴─────┴────────────────┴─────────┘    │
│           D = Details, E = Erase, R = Restore              │
│                                                             │
│  Actions:                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Details  │  │  Erase   │  │ Restore  │                │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘                │
│        │            │              │                       │
└────────┼────────────┼──────────────┼───────────────────────┘
         │            │              │
         ▼            ▼              ▼
    ┌────────┐  ┌──────────┐  ┌──────────┐
    │Details │  │Permanent │  │ Restore  │
    │ Dialog │  │  Delete  │  │   File   │
    └────────┘  └──────────┘  └──────────┘
                      │              │
                      ▼              ▼
                 File removed   Back to
                 forever        Uploaded Files
```

---

## 📈 Timeline Visualization

```
Day 0                                      Day 15
│                                              │
│  File Deleted                               │  Auto-Delete
│  ↓                                          │  ↓
├──────────────────────────────────────────────┤──→ [DELETED]
│                                              │
│  ◄────────── 15 Days Grace Period ──────────►
│
│
├──► Day 1-7:   Normal countdown (white)
│
├──► Day 8-12:  Warning period (yellow) 🟡
│
├──► Day 13-15: Critical period (red) 🔴
│
└──► Day 15+:   Auto-deleted by system
```

---

## 🔢 Age Calculation Logic

```
┌─────────────────────────────────────────────────────────┐
│                 Age Calculation                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  File moved to RecycleBin at: 2025-10-01 10:00:00      │
│  Current time:                2025-10-05 14:30:00      │
│                                                          │
│  Calculation:                                            │
│  ────────────                                            │
│  Age = Current Time - File Modified Time                │
│      = (2025-10-05 14:30:00) - (2025-10-01 10:00:00)   │
│      = 4 days, 4 hours, 30 minutes                      │
│      = 4 days (rounded down)                            │
│                                                          │
│  Days Remaining:                                         │
│  ────────────                                            │
│  Remaining = 15 days - Age                              │
│            = 15 - 4                                      │
│            = 11 days                                     │
│                                                          │
│  Color Code:                                             │
│  ───────────                                             │
│  IF remaining <= 3:  🔴 RED (urgent)                    │
│  IF remaining <= 7:  🟡 YELLOW (warning)                │
│  ELSE:              ⚪ NORMAL                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Decision Tree

```
                    User Action?
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Delete           Restore           Erase
        │                │                │
        ▼                ▼                ▼
   Move to         Restore to      Permanent
  RecycleBin       FileStorage       Delete
        │                │                │
        ▼                ▼                ▼
   Start 15-day      File Active      File Gone
     Timer           Again            Forever
        │                                 
        ▼                                 
  Wait 15 days                           
        │                                 
        ▼                                 
   Auto-Delete                           
        │                                 
        ▼                                 
   File Gone                             
    Forever                              
```

---

## 📊 System State Overview

```
╔═══════════════════════════════════════════════════════════╗
║               DOCUMENT MANAGEMENT SYSTEM                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  FileStorage/                                              ║
║  ├── 📄 active_file1.pdf          (uploaded_files[])     ║
║  ├── 📄 active_file2.docx                                 ║
║  └── RecycleBin/                                          ║
║      ├── 🗑️ deleted1_deleted_20251001.pdf  (15 days)     ║
║      ├── 🗑️ deleted2_deleted_20251003.pdf  (13 days)     ║
║      └── 🗑️ deleted3_deleted_20251005.pdf  (11 days) ✅  ║
║                                                            ║
║  Auto-Cleanup Status: ✅ Active                            ║
║  Next Cleanup: On application restart                      ║
║  Files Pending Auto-Delete: 0                             ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

---

**Visual Guide Version**: 1.0  
**Created**: October 5, 2025  
**Purpose**: Help understand the Recycle Bin system flow

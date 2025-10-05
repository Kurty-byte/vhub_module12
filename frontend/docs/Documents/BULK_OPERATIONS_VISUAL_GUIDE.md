# Bulk Operations - Quick Visual Guide

## 🎨 Button Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  📄 Deleted Files   [🟢 Restore All]  [🔴 Erase All]  [Search...] [🔍] [←]│
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Restore All - Flow Diagram

```
                    Click "Restore All"
                            ↓
        ┌───────────────────────────────────────┐
        │   Check if files exist                │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
   ┌─────────┐                    ┌──────────┐
   │ No files│                    │Files exist│
   └────┬────┘                    └─────┬────┘
        │                               │
        ▼                               ▼
  ┌───────────────┐         ┌────────────────────────┐
  │   Info Dialog │         │  Confirmation Dialog   │
  │"No files to   │         │ "Restore all X files?" │
  │    restore"   │         └──────────┬─────────────┘
  └───────────────┘                    │
                          ┌─────────────┴──────────────┐
                          │                            │
                          ▼                            ▼
                      ┌───────┐                   ┌──────┐
                      │  No   │                   │ Yes  │
                      └───┬───┘                   └──┬───┘
                          │                          │
                          ▼                          ▼
                    ┌──────────┐        ┌────────────────────────┐
                    │  Cancel  │        │ Process each file:     │
                    │  Action  │        │ - Restore file         │
                    └──────────┘        │ - Track success/fail   │
                                        │ - Emit signal          │
                                        └────────┬───────────────┘
                                                 │
                                                 ▼
                                        ┌────────────────────────┐
                                        │  Show Results Dialog   │
                                        │ ✅ Success: X files    │
                                        │ ❌ Failed: Y files     │
                                        └────────┬───────────────┘
                                                 │
                                                 ▼
                                        ┌────────────────────────┐
                                        │   Refresh Table        │
                                        │ (Files now in uploaded)│
                                        └────────────────────────┘
```

---

## 🔴 Erase All - Flow Diagram (Double Confirmation)

```
                    Click "Erase All"
                            ↓
        ┌───────────────────────────────────────┐
        │   Check if files exist                │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
   ┌─────────┐                    ┌──────────┐
   │ No files│                    │Files exist│
   └────┬────┘                    └─────┬────┘
        │                               │
        ▼                               ▼
  ┌───────────────┐       ┌──────────────────────────────┐
  │   Info Dialog │       │  First Confirmation Dialog   │
  │"No files to   │       │  ⚠️  WARNING  ⚠️             │
  │    erase"     │       │"PERMANENTLY delete X files?" │
  └───────────────┘       │"CANNOT be undone!"           │
                          └──────────┬───────────────────┘
                          ┌──────────┴──────────────┐
                          │                         │
                          ▼                         ▼
                      ┌───────┐               ┌──────┐
                      │  No   │               │ Yes  │
                      └───┬───┘               └──┬───┘
                          │                      │
                          ▼                      ▼
                    ┌──────────┐      ┌─────────────────────────┐
                    │  Cancel  │      │ Second Confirmation     │
                    │  Action  │      │ "LAST CHANCE!"          │
                    └──────────┘      │ "X files will be deleted"│
                                      │ "Absolutely sure?"       │
                                      └──────────┬──────────────┘
                                      ┌──────────┴──────────────┐
                                      │                         │
                                      ▼                         ▼
                                  ┌───────┐               ┌──────┐
                                  │  No   │               │ Yes  │
                                  └───┬───┘               └──┬───┘
                                      │                      │
                                      ▼                      ▼
                                ┌──────────┐     ┌────────────────────┐
                                │  Cancel  │     │ Process each file: │
                                │  Action  │     │ - Permanent delete │
                                └──────────┘     │ - Track success    │
                                                 └────────┬───────────┘
                                                          │
                                                          ▼
                                                 ┌────────────────────┐
                                                 │ Show Results Dialog│
                                                 │ ✅ Erased: X files │
                                                 │ ❌ Failed: Y files │
                                                 └────────┬───────────┘
                                                          │
                                                          ▼
                                                 ┌────────────────────┐
                                                 │   Refresh Table    │
                                                 │(Should be empty now)│
                                                 └────────────────────┘
```

---

## 💬 Dialog Examples

### Restore All - Confirmation

```
┌─────────────────────────────────────────┐
│         Confirm Restore All              │
├─────────────────────────────────────────┤
│ Are you sure you want to restore all 5  │
│ deleted file(s)?                         │
│                                          │
│ All files will be moved back to          │
│ uploaded files.                          │
│                                          │
│           [ No ]      [ Yes ]            │
└─────────────────────────────────────────┘
```

### Restore All - Success

```
┌─────────────────────────────────────────┐
│               Success                    │
├─────────────────────────────────────────┤
│ Successfully restored all 5 file(s)!    │
│                                          │
│                 [ OK ]                   │
└─────────────────────────────────────────┘
```

### Restore All - Partial Success

```
┌─────────────────────────────────────────────────┐
│           Partial Success                        │
├─────────────────────────────────────────────────┤
│ Restored: 3 file(s)                             │
│ Failed: 2 file(s)                               │
│                                                  │
│ Errors:                                          │
│ - doc1.pdf: File not found in recycle bin      │
│ - doc2.docx: Permission denied                  │
│                                                  │
│                    [ OK ]                        │
└─────────────────────────────────────────────────┘
```

---

### Erase All - First Confirmation

```
┌─────────────────────────────────────────────────┐
│          Confirm Erase All                       │
├─────────────────────────────────────────────────┤
│           ⚠️  WARNING  ⚠️                       │
│                                                  │
│ Are you sure you want to PERMANENTLY delete     │
│ all 5 file(s)?                                  │
│                                                  │
│ This action CANNOT be undone!                   │
│                                                  │
│ All files will be removed from the Recycle      │
│ Bin forever.                                     │
│                                                  │
│            [ No ]      [ Yes ]                   │
└─────────────────────────────────────────────────┘
```

### Erase All - Second Confirmation

```
┌─────────────────────────────────────────────────┐
│         Final Confirmation                       │
├─────────────────────────────────────────────────┤
│ This is your LAST CHANCE!                       │
│                                                  │
│ 5 file(s) will be permanently deleted.          │
│                                                  │
│ Are you absolutely sure?                        │
│                                                  │
│            [ No ]      [ Yes ]                   │
└─────────────────────────────────────────────────┘
```

### Erase All - Success

```
┌─────────────────────────────────────────────────┐
│               Success                            │
├─────────────────────────────────────────────────┤
│ Successfully erased all 5 file(s) permanently.  │
│                                                  │
│                    [ OK ]                        │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Button Color Codes

### Restore All Button
```
Normal:  🟢 #28a745 (Green)
Hover:   🟢 #218838 (Dark Green)
Action:  Non-destructive, safe
```

### Erase All Button
```
Normal:  🔴 #dc3545 (Red)
Hover:   🔴 #c82333 (Dark Red)
Action:  DESTRUCTIVE, dangerous
```

---

## 📊 Operation Comparison

| Feature | Restore All | Erase All |
|---------|-------------|-----------|
| **Color** | 🟢 Green | 🔴 Red |
| **Action** | Non-destructive | Destructive |
| **Confirmations** | 1 | 2 (double) |
| **Can Undo** | Yes (delete again) | No |
| **Risk Level** | Low | High |
| **Warning Level** | Normal | Strong ⚠️ |
| **Use Frequency** | Often | Rarely |
| **Speed** | ~0.1s/file | ~0.05s/file |

---

## 🔢 Processing Logic

### Restore All
```python
files_to_restore = get_deleted_files()  # e.g., 5 files
success_count = 0
failed_count = 0

FOR EACH file IN files_to_restore:
    result = restore_file(file)
    IF result is success:
        success_count++  # 1, 2, 3...
    ELSE:
        failed_count++
        save_error_message

IF failed_count == 0:
    SHOW "Success: All 5 files restored!"
ELSE:
    SHOW "Restored: 3, Failed: 2"
    SHOW error_messages
```

### Erase All
```python
files_to_erase = get_deleted_files()  # e.g., 5 files

IF user_confirms_first == YES:
    IF user_confirms_second == YES:
        success_count = 0
        failed_count = 0
        
        FOR EACH file IN files_to_erase:
            result = permanent_delete(file)
            IF result is success:
                success_count++
            ELSE:
                failed_count++
                save_error_message
        
        IF failed_count == 0:
            SHOW "Success: All 5 files erased!"
        ELSE:
            SHOW "Erased: 4, Failed: 1"
            SHOW error_messages
```

---

## 🎯 User Decision Tree

```
                User has deleted files
                          │
            ┌─────────────┴─────────────┐
            │                           │
    Want to restore?            Want to erase?
            │                           │
            ▼                           ▼
    ┌───────────────┐           ┌──────────────┐
    │ Restore All   │           │  Erase All   │
    │  (Green)      │           │   (Red)      │
    └───────┬───────┘           └──────┬───────┘
            │                          │
            ▼                          ▼
    ┌───────────────┐           ┌──────────────┐
    │ 1 Confirmation│           │2 Confirmations│
    └───────┬───────┘           └──────┬───────┘
            │                          │
            ▼                          ▼
    ┌───────────────┐           ┌──────────────┐
    │Files restored │           │Files erased  │
    │to uploaded    │           │permanently   │
    └───────────────┘           └──────────────┘
```

---

## ⚡ Keyboard Shortcuts (Future)

```
Ctrl + Shift + R  →  Restore All
Ctrl + Shift + E  →  Erase All (with warnings)
Escape           →  Cancel any dialog
Enter            →  Confirm dialog
```

---

## 📈 Usage Statistics (Expected)

```
╔═════════════════════════════════════════════╗
║         Bulk Operations Usage               ║
╠═════════════════════════════════════════════╣
║                                             ║
║  Restore All:                               ║
║  ████████████████████░░  80% usage          ║
║  Most common: After bulk delete mistakes    ║
║                                             ║
║  Erase All:                                 ║
║  ████░░░░░░░░░░░░░░░░  20% usage            ║
║  Most common: Periodic cleanup              ║
║                                             ║
╚═════════════════════════════════════════════╝
```

---

## ✅ Quick Test Checklist

```
Restore All:
☐ Click button with 0 files → "No files" message
☐ Click button with 3 files → Confirmation shows "3 files"
☐ Confirm Yes → All files restored, table empty
☐ Check uploaded files → All 3 appear there
☐ Test with 1 corrupted file → Partial success message

Erase All:
☐ Click button with 0 files → "No files" message
☐ Click button with 3 files → First warning appears
☐ Cancel first warning → No files deleted
☐ Accept first warning → Second warning appears
☐ Cancel second warning → No files deleted
☐ Accept both warnings → All files permanently deleted
☐ Check RecycleBin/ folder → Empty
☐ Check table → Empty
```

---

**Quick Guide Version**: 1.0  
**Created**: October 5, 2025  
**Feature**: Bulk Operations for Deleted Files

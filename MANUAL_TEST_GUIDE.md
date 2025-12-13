# 🧪 Manual Test Guide - ArchiveService

**Objective:** Verify ότι το ArchiveService refactoring δουλεύει στο Admin

---

## ✅ Pre-Test Checklist

**Syntax Validation:**
- ✅ `archive_service.py` - No syntax errors
- ✅ `models.py` - No syntax errors
- ✅ `obligations.py` (admin) - No syntax errors

**Files Created:**
- ✅ `accounting/services/archive_service.py`
- ✅ `accounting/migrations/10003_remove_attachment_upload_to.py`
- ✅ `templates/accounting/partials/_duplicate_modal.html`
- ✅ `accounting/static/accounting/js/archive.js`

**Files Modified:**
- ✅ `accounting/models.py`
- ✅ `accounting/admin/obligations.py`

---

## 🚀 Test Steps

### **1. Start Django Server**

```bash
# Activate virtual environment (if exists)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

**Expected:** Server starts at http://127.0.0.1:8000/

---

### **2. Open Admin**

1. Navigate to: **http://127.0.0.1:8000/admin/**
2. Login με superuser credentials
3. Navigate to: **Accounting → Monthly Obligations**

---

### **3. Create or Edit Obligation**

**Option A: Create New**
1. Click "Add Monthly Obligation"
2. Fill required fields:
   - Client
   - Obligation Type
   - Year, Month
   - Status
3. **Upload a PDF file** (< 10MB) στο "Συνημμένο Αρχείο" field
4. Click "Save"

**Option B: Edit Existing**
1. Select an existing obligation
2. Upload new PDF file
3. Click "Save"

---

### **4. Verify Results**

#### **A. Success Message** ✅
**Expected:**
```
📁 Το αρχείο αρχειοθετήθηκε: clients/123456789_ACME/2025/01/ΦΠΑ/ΦΠΑ_01_2025.pdf
```

**Check:**
- [ ] Success message displayed at top
- [ ] Message contains full file path
- [ ] Path follows pattern: `clients/{afm}_{name}/{year}/{month}/{type}/filename.pdf`

---

#### **B. File Storage** ✅

**Check file location:**
```bash
# Navigate to media directory
cd media/clients/

# List directories
ls -la

# Expected structure:
# clients/
#   └── {afm}_{client_name}/
#       └── {year}/
#           └── {month}/
#               └── {type_code}/
#                   └── {filename}.pdf
```

**Verify:**
- [ ] Client folder created: `{afm}_{name}`
- [ ] Year folder exists: `2025`
- [ ] Month folder exists: `01`, `02`, etc.
- [ ] Type folder exists: `ΦΠΑ`, `ΑΠΔ`, etc.
- [ ] PDF file exists inside

---

#### **C. Database Update** ✅

**Check obligation record:**
1. In Admin, open the obligation again
2. Look at "Συνημμένο Αρχείο" field

**Verify:**
- [ ] Shows filename (clickable link)
- [ ] Path matches the created folder structure
- [ ] Can download the file

**Via Django Shell:**
```python
python manage.py shell

from accounting.models import MonthlyObligation

# Get latest obligation
obl = MonthlyObligation.objects.latest('id')

# Check attachment path
print(obl.attachment.name)
# Expected: clients/{afm}_{name}/2025/01/ΦΠΑ/ΦΠΑ_01_2025.pdf

# Check it's not using old upload_to pattern
# OLD pattern would be: random_chars_filename.pdf
# NEW pattern is: organized structure
```

---

#### **D. Admin Behavior** ✅

**Test duplicate upload:**
1. Edit the same obligation again
2. Upload **another PDF with same name**
3. Click "Save"

**Expected (Admin uses 'replace' strategy):**
- [ ] File replaced without prompt
- [ ] Success message: "Αρχειοθετήθηκε"
- [ ] No modal/popup
- [ ] Old file overwritten

---

## ⚠️ Error Scenarios to Test

### **1. Non-PDF File**

**Steps:**
1. Try to upload `.docx`, `.txt`, or `.jpg`
2. Click "Save"

**Expected:**
- ❌ Validation error OR
- ⚠️ Warning message: "Επιτρέπονται μόνο αρχεία PDF για υποχρεώσεις"

---

### **2. Oversized File**

**Steps:**
1. Upload PDF > 10MB
2. Click "Save"

**Expected:**
- ⚠️ Warning: "Το αρχείο υπερβαίνει τα 10MB"

---

### **3. No File Upload**

**Steps:**
1. Create/edit obligation WITHOUT uploading file
2. Click "Save"

**Expected:**
- ✅ Saves normally
- ℹ️ No archive message (only shows if file uploaded)

---

## 🐛 Known Issues to Watch For

### **Issue 1: Circular Import**
**Symptom:**
```
ImportError: cannot import name 'ArchiveService' from partially initialized module
```

**Fix:**
Move import inside method (already done in models.py)

---

### **Issue 2: `upload_to` Still Called**
**Symptom:**
File saved to wrong location (old pattern)

**Cause:**
Migration not applied

**Fix:**
```bash
python manage.py migrate accounting 10003
```

---

### **Issue 3: `archive_attachment()` Fails**
**Symptom:**
```
⚠️ Σφάλμα αρχειοθέτησης: ...
```

**Debug:**
```python
# Check logs
tail -f logs/django.log

# Or add print debugging:
# In admin/obligations.py, line ~600
print(f"DEBUG: Uploaded file: {obj.attachment}")
print(f"DEBUG: File object: {obj.attachment.file}")
```

---

## ✅ Success Criteria

**All of these should be TRUE:**

- [x] **Syntax checks passed** (already verified)
- [ ] Server starts without errors
- [ ] Admin loads normally
- [ ] Can create/edit MonthlyObligation
- [ ] File upload works
- [ ] Success message shows correct path
- [ ] File stored in organized structure
- [ ] attachment.name updated in database
- [ ] Can download uploaded file
- [ ] Duplicate upload replaces old file

---

## 📊 Test Results Template

```markdown
## Test Results - [Date]

### Environment:
- Python version:
- Django version:
- Browser:

### Tests Performed:

#### Upload New File
- [ ] PASS / FAIL
- Path created:
- Message:
- Issues:

#### Duplicate Upload
- [ ] PASS / FAIL
- Behavior:
- Issues:

#### Error Handling
- [ ] Non-PDF rejection: PASS / FAIL
- [ ] Size limit: PASS / FAIL

### Overall Status:
- [ ] ✅ Ready to proceed with views refactoring
- [ ] ⚠️ Issues found (describe below)
- [ ] ❌ Critical failures (stop and fix)

### Notes:
```

---

## 🚀 Next Steps After Testing

**If tests PASS:**
✅ Proceed with views refactoring (8 upload points)

**If tests FAIL:**
1. Document the failure in test results
2. Share error messages/logs
3. Fix issues before continuing
4. Re-test

---

**Prepared by:** Claude Code
**Date:** 2025-12-13

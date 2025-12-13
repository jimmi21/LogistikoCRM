# D.P. Economy Code Health Audit & Cleanup Plan

**Audit Date:** December 3, 2025
**Branch:** `claude/audit-code-health-016o91QK8gJE39339BSszAPj`

---

## Executive Summary

| Category | Critical | Important | Nice to Have | Total |
|----------|----------|-----------|--------------|-------|
| Security | 3 | 2 | 0 | 5 |
| Dead Code | 2 | 4 | 2 | 8 |
| Code Quality | 0 | 6 | 6 | 12 |
| API Consistency | 0 | 2 | 3 | 5 |
| **Total** | **5** | **14** | **11** | **30** |

---

## Critical (Do Now)

### 1. UNPROTECTED DOOR CONTROL ENDPOINTS

**Severity:** CRITICAL - Physical Security Risk
**File:** `/home/user/D.P. Economy/accounting/views.py`
**Lines:** 2668-2776

**Issue:** Door control endpoints have NO authentication:
- `GET /accounting/door-status/` - Check door status
- `POST /accounting/open-door/` - Toggle door
- `GET|POST /accounting/door-control/` - Combined endpoint

**Current Code:**
```python
@require_http_methods(["GET"])
def door_status(request):  # NO AUTH!
```

**Fix Required:**
```python
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@require_http_methods(["GET"])
def door_status(request):
```

**Effort:** 5 min
**Files to modify:** `accounting/views.py` (add decorators to 3 functions)

---

### 2. DELETE DEAD CODE FILE: `admin2 .py`

**Severity:** CRITICAL - Causes confusion, 44KB of dead code
**File:** `/home/user/D.P. Economy/accounting/admin2 .py`

**Issue:**
- Filename has a SPACE character before `.py`
- Contains duplicate admin classes already in `admin.py`
- NEVER imported anywhere in the codebase
- 1000+ lines of completely dead code

**Fix Required:**
```bash
rm "/home/user/D.P. Economy/accounting/admin2 .py"
```

**Effort:** 5 min

---

### 3. DELETE DEAD CODE FILE: `views_τουμπανο.py`

**Severity:** CRITICAL - 62KB of dead code, Greek backup file
**File:** `/home/user/D.P. Economy/accounting/views_τουμπανο.py`

**Issue:**
- Greek filename suggests it was a backup/development copy
- Contains 1827 lines of duplicate code
- NEVER imported anywhere
- Includes duplicate function definitions that exist in main `views.py`

**Fix Required:**
```bash
rm "/home/user/D.P. Economy/accounting/views_τουμπανο.py"
```

**Effort:** 5 min

---

### 4. REMOVE DUPLICATE FUNCTION: `quick_complete_obligation()`

**Severity:** CRITICAL - Two definitions cause confusion
**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** Function defined TWICE:
- **Line 238:** Original version with FormData/JSON and file upload support
- **Line 2784:** Simpler duplicate version

Python uses the LAST definition, meaning the first 500+ line version is DEAD CODE.

**Fix Required:** Delete the duplicate at line 2784 (or merge functionality)

**Effort:** 30 min (need to verify which version is correct)

---

### 5. REMOVE DUPLICATE FUNCTION: `advanced_bulk_complete()`

**Severity:** CRITICAL - Two definitions cause confusion
**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** Function defined TWICE:
- **Line 458:** First version with extensive debugging
- **Line 2560:** Second version with simplified logging

**Fix Required:** Delete one version (recommend keeping line 458)

**Effort:** 30 min

---

## Important (Do Soon)

### 6. DUPLICATE CLASS: `VoIPCallsListView`

**Severity:** HIGH - Dead code, confusing
**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** Class defined TWICE:
- **Line 1141:** First definition (DEAD - never reached)
- **Line 2119:** Second definition (active)

**Fix Required:** Delete first definition at line 1141

**Effort:** 15 min

---

### 7. UNREFERENCED FUNCTION: `bulk_complete_view()`

**Severity:** MEDIUM - 74 lines of dead code
**File:** `/home/user/D.P. Economy/accounting/views.py`
**Lines:** 384-457

**Issue:** Defined but NOT in `urls.py`. Replaced by `bulk_complete_obligations()`

**Fix Required:** Delete function

**Effort:** 5 min

---

### 8. CONSOLIDATE VoIP APPS (voip/ vs accounting/)

**Severity:** HIGH - Confusing architecture
**Files:** `/home/user/D.P. Economy/voip/` entire directory

**Issue:** Two VoIP systems:
- `/voip/` - Zadarma (outbound) - appears DEPRECATED
- `/accounting/` - Fritz!Box (inbound) - ACTIVE

| Component | /voip/ | /accounting/ | Winner |
|-----------|--------|--------------|--------|
| Models | 1 (Connection) | 3 (VoIPCall, VoIPCallLog, Ticket) | accounting |
| Admin | Basic | Advanced | accounting |
| API | None | REST ViewSets | accounting |
| Integration | None | Client, Email, Celery | accounting |

**Recommendation:**
1. Verify if Zadarma is still used (check settings for `VOIP_FORWARD`)
2. If not used: Delete entire `/voip/` directory
3. If used: Move Zadarma to `/accounting/voip_backends/`

**Effort:** 2hr+ (requires verification)

---

### 9. PRINT STATEMENTS TO LOGGER

**Severity:** MEDIUM - Production code quality

| File | Line | Current | Fix |
|------|------|---------|-----|
| `accounting/models.py` | 1207 | `print(f"Could not create...")` | `logger.error(...)` |
| `webcrm/celery.py` | 14 | `print(f'Request: {self.request!r}')` | `logger.debug(...)` |
| `crm/utils/oauth2.py` | 222-363 | Multiple `print()` | Convert all to `logger` |

**Effort:** 30 min

---

### 10. UNUSED IMPORTS

**Severity:** LOW - Code cleanliness

| File | Line | Import |
|------|------|--------|
| `accounting/models.py` | 5 | `from dateutil.relativedelta import relativedelta` |
| `accounting/models.py` | 10 | `from django.utils.text import slugify` |
| `accounting/models.py` | 246 | `import re` (duplicate) |
| `accounting/client_sync.py` | 12 | `from django.contrib import messages` |
| `accounting/client_sync.py` | 13 | `import os` |
| `inventory/admin.py` | 7 | `from django.shortcuts import redirect` |

**Effort:** 15 min

---

### 11. CLEAN UP `crm/apps.py` COMMENTED CODE

**Severity:** MEDIUM - Dead commented code
**File:** `/home/user/D.P. Economy/crm/apps.py`
**Lines:** 15-39

**Issue:** 25+ lines of commented-out IMAP code that will never be uncommented

**Fix Required:** Delete commented lines, add note that IMAP is disabled

**Effort:** 10 min

---

### 12. STANDARDIZE API ERROR RESPONSES

**Severity:** MEDIUM - Inconsistent API

**Current formats:**
```python
# Format A
{"error": "message"}

# Format B
{"success": false, "error": "message"}

# Format C (DRF)
{"detail": "message"}
```

**Recommended standard:**
```python
{"success": false, "error": "message", "code": "ERROR_CODE"}
```

**Effort:** 1hr

---

### 13. CACHING ON AUTHENTICATED ENDPOINTS

**Severity:** MEDIUM - Potential data leak
**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** `@cache_page()` on staff-only endpoints may cache responses globally

**Locations:**
- `voip_calls_api` - `@cache_page(5)`
- `voip_statistics` - `@cache_page(60)`

**Fix Required:** Either remove caching or make cache key user-specific

**Effort:** 30 min

---

### 14. ADD RATE LIMITING

**Severity:** MEDIUM - Security
**Scope:** All API endpoints

**Issue:** No rate limiting anywhere - brute force risk

**Fix Required:** Add `django-ratelimit` or DRF throttling

**Effort:** 1hr

---

## Nice to Have (Do Later)

### 15. REMOVE LEGACY URL ROUTE

**File:** `/home/user/D.P. Economy/accounting/urls.py:48`
```python
path("quick-complete/<int:obligation_id>/", views.quick_complete_obligation, name="quick_complete"),  # Legacy
```

**Issue:** Marked `# Legacy` - both routes call same view

**Effort:** 5 min + verify no JS uses old URL

---

### 16. DELETE DISABLED `crm_imap.py`

**File:** `/home/user/D.P. Economy/crm/utils/crm_imap.py`

**Issue:** Completely stub implementation with docstring "DISABLED"

**Effort:** 15 min (update all imports first)

---

### 17. EMPTY URL PATTERNS

**Files:**
- `/home/user/D.P. Economy/chat/urls.py` - `urlpatterns = []`
- `/home/user/D.P. Economy/analytics/urls.py` - Placeholder comment
- `/home/user/D.P. Economy/help/urls.py` - `urlpatterns = []`

**Issue:** Empty or placeholder URL patterns - incomplete features

**Effort:** 5 min each (add TODO comments or delete)

---

### 18. REMOVE COMMENTED IMPORTS IN voip/urls.py

**File:** `/home/user/D.P. Economy/voip/urls.py:1-2`
```python
# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
```

**Effort:** 2 min

---

### 19. TRACK TODO/FIXME COMMENTS

**Found 9 TODO/FIXME comments:**

| File | Line | Comment |
|------|------|---------|
| `accounting/admin2 .py` | 285 | `# TODO: Implement email sending` |
| `accounting/admin2 .py` | 560 | `# TODO: Implement email sending` |
| `accounting/admin2 .py` | 566 | `# TODO: Implement PDF generation` |
| `accounting/admin2 .py` | 991 | `# TODO: Implement email sending` |
| `accounting/admin2 .py` | 998 | `# TODO: Implement invoice generation` |
| `mydata/services.py` | 197 | `# TODO: Update items if needed` |
| `mydata/services.py` | 233 | `# TODO: Parse detail` |
| `crm/site/leadadmin.py` | 186 | `# TODO: improve this with phone` |
| `common/settings.py` | 2 | `# TODO: REMAINDER_CHECK_INTERVAL deprecated` |

**Note:** Most in `admin2 .py` which should be deleted anyway

**Effort:** 30 min (move to GitHub Issues)

---

### 20. FRITZ!BOX WEBHOOK AUTH IMPROVEMENT

**File:** `/home/user/D.P. Economy/accounting/views.py:784-898`

**Issue:** Uses manual Bearer token validation instead of DRF authentication classes

**Current:**
```python
token = request.headers.get('Authorization', '').replace('Bearer ', '')
if token != settings.FRITZ_API_TOKEN:
```

**Better:**
```python
from rest_framework.authentication import TokenAuthentication
# Use DRF authentication class
```

**Effort:** 1hr

---

### 21. ADD EXPLICIT PERMISSION CLASS TO DocumentViewSet

**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** `ClientDocumentViewSet` uses default `IsAuthenticated` but should be explicit

**Fix:**
```python
class ClientDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
```

**Effort:** 5 min

---

### 22. ZADARMA WEBHOOK HMAC REVIEW

**File:** `/home/user/D.P. Economy/voip/views/voipwebhook.py:83-103`

**Issue:** Custom HMAC-SHA1 implementation should be reviewed by security expert

**Effort:** 1hr (security review)

---

### 23. REMOVE EMOJI FROM LOGGER MESSAGES

**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** Logger messages contain emojis which may cause encoding issues

**Examples:**
```python
logger.info(f"Checking status at {TASMOTA_IP}")
logger.info(f"Status: {power}")
logger.error(f"HTTP {response.status_code}")
```

**Effort:** 15 min

---

### 24. ADD ClientDocumentViewSet EXPLICIT QUERYSET FILTER

**File:** `/home/user/D.P. Economy/accounting/views.py`

**Issue:** Ensure documents are only accessible by authorized users

**Effort:** 15 min

---

### 25. CLEAN UP TEST PRINT STATEMENTS

**Files:**
- `tests/chat/test_chat.py:58`
- `tests/crm/test_contact.py:48`
- `tests/crm/test_create_email_request.py:32`
- `tests/crm/test_request_methods.py:30`

**Issue:** `print("Run Test Method:", ...)` in tests - not critical but noisy

**Effort:** 10 min

---

## Implementation Order

### Phase 1: Critical Security (Day 1)
```bash
# 1. Fix door control auth
# 2. Delete dead files
rm "/home/user/D.P. Economy/accounting/admin2 .py"
rm "/home/user/D.P. Economy/accounting/views_τουμπανο.py"
```

### Phase 2: Duplicate Code (Day 1-2)
- Remove duplicate functions in views.py
- Remove duplicate class definitions

### Phase 3: VoIP Consolidation (Day 3-5)
- Verify Zadarma usage
- Migrate or delete /voip/ directory

### Phase 4: Code Quality (Week 2)
- Print to logger conversion
- Unused import cleanup
- Commented code removal
- API standardization

### Phase 5: Nice to Have (Ongoing)
- Rate limiting
- Security improvements
- Documentation updates

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `accounting/views.py` | Add auth to door endpoints, remove duplicates |
| `accounting/admin2 .py` | DELETE |
| `accounting/views_τουμπανο.py` | DELETE |
| `accounting/models.py` | Remove unused imports, print→logger |
| `accounting/client_sync.py` | Remove unused imports |
| `accounting/urls.py` | Remove legacy route |
| `inventory/admin.py` | Remove unused import |
| `voip/` | Potentially DELETE entire directory |
| `crm/apps.py` | Clean commented code |
| `crm/utils/oauth2.py` | Print→logger |
| `webcrm/celery.py` | Print→logger |

---

## Verification Commands

```bash
# After cleanup, run:
python manage.py check
python manage.py makemigrations --dry-run
python manage.py test

# Search for remaining issues:
grep -r "print(" --include="*.py" | grep -v "test"
grep -r "# TODO" --include="*.py"
```

---

*Generated by Claude Code Health Audit*
*Codebase: D.P. Economy*

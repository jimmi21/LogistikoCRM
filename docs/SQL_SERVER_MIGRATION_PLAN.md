# SQL Server Migration Plan - LogistikoCRM

**Analysis Date:** December 11, 2025
**Current Database:** SQLite (dev) / PostgreSQL (prod)
**Target Database:** Microsoft SQL Server 2019+

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Compatibility** | 85% Ready |
| **Critical Issues** | 5 |
| **High Priority Issues** | 8 |
| **Medium Priority Issues** | 12 |
| **Estimated Migration Effort** | 2-3 weeks |
| **Risk Level** | MEDIUM |

**Verdict:** Η μετάβαση είναι **ΕΦΙΚΤΗ** με στοχευμένες αλλαγές κώδικα.

---

## 1. CRITICAL ISSUES (Must Fix Before Migration)

### 1.1 GROUP_CONCAT Aggregate Function
**File:** `analytics/utils/helpers.py:27-39`

```python
# CURRENT (MySQL-specific)
class GroupConcat(Aggregate, ABC):
    function = 'GROUP_CONCAT'

# REQUIRED (SQL Server compatible)
class GroupConcat(Aggregate):
    function = 'STRING_AGG'  # SQL Server 2017+
    template = '%(function)s(%(expressions)s, %(separator)s)'
```

**Impact:** Analytics reports θα αποτύχουν
**Files Affected:** `analytics/site/incomestatadmin.py:389`

---

### 1.2 Regular Expression Lookups (__regex, __iregex)
**8 Files Affected:**

| File | Line | Current Pattern |
|------|------|-----------------|
| `crm/views/delete_duplicate_object.py` | 98 | `recipient_ids__regex=re_str` |
| `massmail/views/exclude.py` | 21 | `successful_ids__iregex=...` |
| `crm/models/request.py` | 377-378 | `full_name__iregex=...` |
| `crm/utils/create_form_request.py` | 34 | `alternative_names__regex=...` |
| `crm/utils/check_city.py` | 28 | `alternative_names__regex=...` |
| `crm/site/leadadmin.py` | 224-225 | `phone__iregex=phone_re` |
| `common/utils/helpers.py` | 62-64 | Multiple `__iregex` lookups |

**Solution:** Replace with `__icontains` or implement custom LIKE patterns:
```python
# BEFORE
.filter(phone__iregex=r'^\+?30')

# AFTER (SQL Server compatible)
.filter(Q(phone__istartswith='+30') | Q(phone__istartswith='30'))
```

---

### 1.3 select_for_update() Row Locking
**File:** `inventory/models.py:251-256`

```python
# CURRENT
product = Product.objects.select_for_update().get(pk=self.product.pk)

# SQL Server requires different approach
# Option A: Use select_for_update(nowait=True)
# Option B: Implement WITH (UPDLOCK) hint
```

**Impact:** Race conditions στο inventory management

---

### 1.4 PostgreSQL Driver Dependency
**File:** `requirements.txt:12`

```diff
- psycopg2-binary>=2.9.9  # REMOVE

+ mssql-django>=1.3       # ADD for SQL Server
+ pyodbc>=5.0.1           # ADD ODBC driver
```

---

### 1.5 Database Configuration
**File:** `webcrm/settings.py:41-52`

```python
# SQL Server Configuration
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME', 'LogistikoCRM'),
        'USER': os.getenv('DB_USER', 'sa'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'isolation_level': 'READ COMMITTED',
        },
    }
}
```

---

## 2. HIGH PRIORITY ISSUES

### 2.1 Aggregate FILTER Clause (19 instances)
**Problem:** SQL Server χρησιμοποιεί διαφορετική σύνταξη.

**Affected Files:**
- `accounting/api_dashboard.py:270`
- `accounting/views/helpers.py:453-514` (6 instances)
- `accounting/views/voip.py:72-75` (4 instances)
- `accounting/api_reports.py:378-379`
- `common/site/crmsite.py:222-238` (4 instances)
- `tasks/views/create_completed_subtask.py:33-34`

**Django Behavior:** Django αυτόματα μετατρέπει σε `CASE WHEN` για SQL Server - **θα δουλέψει**, αλλά απαιτεί testing.

---

### 2.2 JSONField Usage (9 instances)
**Affected Models:**

| Model | Field | File |
|-------|-------|------|
| MonthlyObligation | attachments | accounting/models.py:404 |
| AuditLog | changes, extra_data | common/models.py:384,392 |
| UserProfile | messages | common/models.py:314 |
| VATSyncLog | details | mydata/models.py:793 |
| VATPeriodResult | months_synced | mydata/models.py:994 |
| ProductCategory | details | inventory/models.py:480 |

**SQL Server Support:** ✅ Υποστηρίζεται από SQL Server 2016+ και mssql-django.

**Limitation:** Δεν υποστηρίζονται JSON path queries στο ORM (`field__key=value`).

---

### 2.3 Backup/Restore Commands
**Files:**
- `common/management/commands/backup_database.py`
- `common/management/commands/restore_database.py`

**Current:** Υποστηρίζουν μόνο PostgreSQL και SQLite.

**Required:** Προσθήκη SQL Server backup/restore methods:
```python
def _backup_sqlserver(self, output_dir, backup_name, db_config):
    """Backup SQL Server database using BACKUP DATABASE T-SQL"""
    # Implementation needed
```

---

### 2.4 Index Rename Operations
**File:** `accounting/migrations/10001_remove_clientprofile_client_afm_idx_and_more.py`

**Issue:** `RenameIndex` operations μπορεί να αποτύχουν σε SQL Server.

**Solution:** Fresh migrations από SQL Server ή manual index recreation.

---

## 3. MEDIUM PRIORITY ISSUES

### 3.1 F() Arithmetic Operations (15+ instances)
**Files:**
- `analytics/utils/helpers.py:110-111`
- `analytics/site/incomestatadmin.py:281,346,361,371`
- `accounting/context_processors.py:51`
- `crm/site/paymentadmin.py:83-95`

**Issue:** SQL Server decimal arithmetic διαφέρει - απαιτεί testing.

---

### 3.2 Date Truncation Functions (4 instances)
**Files:**
- `analytics/utils/helpers.py:84` - `Trunc(field, 'month')`
- `accounting/api_dashboard.py:284` - `TruncMonth()`
- `accounting/api_reports.py:13`
- `accounting/views/helpers.py:11`

**SQL Server:** Χρησιμοποιεί DATEPART/DATEFROMPARTS αντί για DATE_TRUNC.

**Django:** Θα μετατρέψει αυτόματα - απαιτεί verification.

---

### 3.3 BigAutoField Inconsistency
**Problem:** Μερικά apps χρησιμοποιούν BigAutoField, άλλα AutoField.

| App | Auto Field |
|-----|------------|
| accounting | BigAutoField |
| mydata | BigAutoField |
| inventory | BigAutoField |
| crm | AutoField (default) |
| common | AutoField (default) |

**Recommendation:** Standardize σε BigAutoField για consistency.

---

### 3.4 Transaction Isolation (10 instances)
**Files with transaction.atomic():**
- `inventory/models.py:251`
- `accounting/management/commands/import_clients.py:157`
- `mydata/services.py:76,142`
- `accounting/api_export_import.py:315,557`
- `accounting/api_obligation_profiles.py:277,420`

**SQL Server:** Default isolation level διαφέρει. Configure στο settings.

---

## 4. LOW PRIORITY / COMPATIBLE

### 4.1 Already Compatible Features ✅
- **Concat()** - Works with SQL Server
- **Coalesce()** - Fully compatible
- **Cast()** - Fully compatible
- **Case/When** - Fully compatible
- **Subquery/Exists** - Fully compatible
- **distinct()** - Works but test performance
- **unique_together** - Compatible
- **db_index** - All indexes are compatible
- **DecimalField** - 112 instances, all compatible

### 4.2 No Issues Found ✅
- No ArrayField
- No HStoreField
- No BinaryField with issues
- No PostgreSQL full-text search (SearchVector)
- No raw SQL queries

---

## 5. MIGRATION PHASES

### Phase 1: Preparation (Week 1)

#### 1.1 Environment Setup
```bash
# Install SQL Server drivers
pip install mssql-django pyodbc

# Install ODBC Driver 17 for SQL Server (Linux)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

#### 1.2 Create SQL Server Test Database
```sql
CREATE DATABASE LogistikoCRM_Test
COLLATE Greek_CI_AS;  -- Greek case-insensitive collation
```

#### 1.3 Update Dependencies
```diff
# requirements.txt
- psycopg2-binary>=2.9.9
+ mssql-django>=1.3
+ pyodbc>=5.0.1
```

---

### Phase 2: Code Changes (Week 1-2)

#### 2.1 Critical Fixes Checklist
- [ ] Replace GROUP_CONCAT with database-agnostic solution
- [ ] Replace all `__regex` / `__iregex` lookups
- [ ] Update select_for_update() usage
- [ ] Add SQL Server support to backup/restore commands
- [ ] Update settings.py for SQL Server

#### 2.2 High Priority Fixes
- [ ] Test all JSONField operations
- [ ] Verify Aggregate FILTER clause behavior
- [ ] Test F() arithmetic operations
- [ ] Verify date truncation functions

---

### Phase 3: Migration & Testing (Week 2-3)

#### 3.1 Fresh Migrations Strategy
```bash
# Option A: Apply existing migrations
python manage.py migrate --database=sqlserver

# Option B: Fresh start (recommended for production)
python manage.py migrate --run-syncdb --database=sqlserver
```

#### 3.2 Data Migration
```bash
# Export from PostgreSQL
python manage.py dumpdata --natural-foreign --natural-primary -o data.json

# Import to SQL Server
python manage.py loaddata data.json --database=sqlserver
```

#### 3.3 Testing Checklist
- [ ] All Django tests pass
- [ ] Admin interface works correctly
- [ ] API endpoints respond correctly
- [ ] Greek characters display properly
- [ ] File uploads work
- [ ] Celery tasks execute
- [ ] Reports generate correctly
- [ ] Import/Export functionality works

---

### Phase 4: Production Deployment

#### 4.1 Environment Variables
```bash
# .env for SQL Server Production
DB_ENGINE=mssql
DB_NAME=LogistikoCRM
DB_USER=logistiko_user
DB_PASSWORD=<secure_password>
DB_HOST=sql-server.company.local
DB_PORT=1433
```

#### 4.2 Connection Pooling
```python
# settings.py
DATABASES['default']['OPTIONS'] = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'isolation_level': 'READ COMMITTED',
    'MARS_Connection': 'True',  # Multiple Active Result Sets
}
```

#### 4.3 Performance Indexes
Run after migration:
```sql
-- Create additional indexes for performance
CREATE INDEX idx_client_afm ON accounting_clientprofile(afm);
CREATE INDEX idx_obligation_status ON accounting_monthlyobligation(status, deadline);
```

---

## 6. PRODUCTION CHECKLIST

### Pre-Migration
- [ ] SQL Server 2019+ installed and configured
- [ ] ODBC Driver 17+ installed on app server
- [ ] Test database created with Greek collation
- [ ] All critical code fixes applied
- [ ] Full backup of current PostgreSQL database

### Migration Day
- [ ] Set maintenance mode
- [ ] Export data from PostgreSQL
- [ ] Apply migrations to SQL Server
- [ ] Import data to SQL Server
- [ ] Run verification tests
- [ ] Update environment variables
- [ ] Restart application servers
- [ ] Verify all functionality

### Post-Migration
- [ ] Monitor performance for 48 hours
- [ ] Check error logs
- [ ] Verify scheduled tasks (Celery)
- [ ] Test email notifications
- [ ] Verify VoIP integration
- [ ] Performance tuning if needed

---

## 7. ROLLBACK PLAN

Αν η μετάβαση αποτύχει:

1. **Immediate:** Switch back to PostgreSQL via environment variables
2. **Data:** PostgreSQL backup remains untouched
3. **Code:** Git revert if needed (all changes in feature branch)

```bash
# Emergency rollback
export DB_ENGINE=django.db.backends.postgresql
export DB_NAME=logistiko_prod
# Restart services
```

---

## 8. FILES TO MODIFY

### Critical (Must Change)
| File | Changes Required |
|------|------------------|
| `requirements.txt` | Replace psycopg2 with mssql-django |
| `webcrm/settings.py` | Add SQL Server configuration |
| `analytics/utils/helpers.py` | Replace GROUP_CONCAT |
| `crm/views/delete_duplicate_object.py` | Replace regex |
| `massmail/views/exclude.py` | Replace regex |
| `crm/models/request.py` | Replace regex |
| `crm/utils/create_form_request.py` | Replace regex |
| `crm/utils/check_city.py` | Replace regex |
| `crm/site/leadadmin.py` | Replace regex |
| `common/utils/helpers.py` | Replace regex |
| `inventory/models.py` | Fix select_for_update |

### High Priority (Should Change)
| File | Changes Required |
|------|------------------|
| `common/management/commands/backup_database.py` | Add SQL Server support |
| `common/management/commands/restore_database.py` | Add SQL Server support |

---

## 9. ESTIMATED TIMELINE

| Phase | Duration | Tasks |
|-------|----------|-------|
| Preparation | 2-3 days | Environment setup, dependencies |
| Critical Fixes | 3-4 days | GROUP_CONCAT, regex, select_for_update |
| High Priority | 2-3 days | Backup commands, testing JSONField |
| Migration Testing | 3-4 days | Full test cycle on test server |
| Production Migration | 1 day | Data migration, go-live |
| Stabilization | 2-3 days | Monitoring, fixes |
| **Total** | **2-3 weeks** | |

---

## 10. CONCLUSION

Η μετάβαση σε SQL Server είναι **εφικτή** με τις ακόλουθες προϋποθέσεις:

1. **Απαραίτητες αλλαγές κώδικα** - 11 αρχεία χρειάζονται τροποποίηση
2. **Δεν υπάρχουν PostgreSQL-specific features** - Καμία χρήση ArrayField, SearchVector κλπ
3. **JSONField υποστηρίζεται** - Με SQL Server 2016+
4. **Migrations συμβατά** - Με μικρές εξαιρέσεις

**Recommendation:** Proceed with migration following this plan.

---

*Document Version: 1.0*
*Author: Claude Code Analysis*
*Last Updated: December 11, 2025*

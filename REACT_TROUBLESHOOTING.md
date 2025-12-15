# 🚨 React Frontend - Troubleshooting Guide

## ❌ Πρόβλημα: "Network Error" στο Login

Βλέπεις το μήνυμα **"Network Error"** και στο browser console:
```
ERR_BLOCKED_BY_CLIENT
Failed to load resource: net::ERR_BLOCKED_BY_CLIENT
```

---

## 🔍 Αιτίες & Λύσεις

### 1️⃣ **Ad Blocker / Privacy Extension (Πιο Συχνό)**

**Πρόβλημα:** Το browser extension μπλοκάρει το API request.

**Λύση:**

#### A. Απενεργοποίησε προσωρινά το ad blocker
- **uBlock Origin:** Κλικ στο εικονίδιο → "Disable on this site"
- **AdBlock Plus:** Κλικ → "Pause AdBlock on this site"
- **Privacy Badger:** Κλικ → Disable

#### B. Πρόσθεσε εξαίρεση (whitelist)
Πρόσθεσε τα εξής στη λίστα εξαιρέσεων:
```
http://localhost:8000
http://localhost:3000
http://127.0.0.1:8000
http://127.0.0.1:3000
```

#### C. Ανοιξε σε Incognito Mode (για δοκιμή)
- **Chrome:** Ctrl+Shift+N
- **Firefox:** Ctrl+Shift+P
- Τα extensions είναι απενεργοποιημένα by default

---

### 2️⃣ **Το Django Backend Δεν Τρέχει**

**Πρόβλημα:** Το React frontend προσπαθεί να συνδεθεί στο `localhost:8000` αλλά δεν υπάρχει server.

**Λύση:**

#### Εκκίνησε το Django Server:

```bash
# Terminal 1 - Django Backend
cd /home/user/LogistikoCRM
source venv/bin/activate  # ή venv\Scripts\activate (Windows)

# Βεβαιώσου ότι το DEBUG=True στο .env
echo "DEBUG=True" >> .env

# Εκκίνησε το server
python manage.py runserver 0.0.0.0:8000
```

Θα πρέπει να δεις:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

#### Εκκίνησε το React Frontend (σε άλλο terminal):

```bash
# Terminal 2 - React Frontend
cd /home/user/LogistikoCRM/frontend
npm install  # πρώτη φορά μόνο
npm start    # ή npm run dev
```

Θα πρέπει να δεις:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
```

---

### 3️⃣ **CORS Configuration Issue**

**Πρόβλημα:** Το Django δεν επιτρέπει requests από το React.

**Λύση:**

#### Έλεγξε το `.env` file:
```bash
# Δημιούργησε/επεξεργάσου το .env
nano .env  # ή vim/code
```

Πρόσθεσε:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
```

#### Επιβεβαίωση CORS στο `webcrm/settings.py`:

```python
# Αυτά πρέπει να υπάρχουν (ήδη ρυθμισμένα):
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Επιτρέπει όλες τις origins αν DEBUG=True
CORS_ALLOW_CREDENTIALS = True
```

---

### 4️⃣ **Λάθος Port / URL**

**Πρόβλημα:** Το React χρησιμοποιεί λάθος URL για το backend.

**Λύση:**

#### Έλεγξε το `frontend/.env`:

```bash
cd frontend
cat .env  # δες αν υπάρχει
```

Αν δεν υπάρχει ή είναι λάθος, δημιούργησέ το:

```env
VITE_API_URL=http://localhost:8000/accounting
```

#### Για τοπικό δίκτυο (αν θέλεις πρόσβαση από άλλο PC):

```env
VITE_API_URL=http://192.168.1.100:8000/accounting
```

*(Αντικατάστησε το `192.168.1.100` με το πραγματικό σου IP)*

---

## ✅ Πλήρης Οδηγός Εκκίνησης

### Βήμα 1: Βεβαιώσου ότι υπάρχει το .env

```bash
cd /home/user/LogistikoCRM
cat .env

# Αν δεν υπάρχει, δημιούργησέ το:
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-for-development
DB_ENGINE=django.db.backends.sqlite3
EMAIL_BACKEND_CONSOLE=true
EOF
```

### Βήμα 2: Εκκίνησε τα δύο servers

**Terminal 1 - Django:**
```bash
cd /home/user/LogistikoCRM
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - React:**
```bash
cd /home/user/LogistikoCRM/frontend
npm install  # πρώτη φορά
npm start
```

### Βήμα 3: Απενεργοποίησε Ad Blockers

- uBlock Origin
- AdBlock Plus
- Privacy Badger
- Brave Shields

### Βήμα 4: Δοκίμασε το Login

Άνοιξε: `http://localhost:3000` (ή ό,τι port δείχνει το Vite)

Credentials (αν έχεις κάνει `createsuperuser`):
- Username: `ddiplas` (ή ό,τι έδωσες)
- Password: (το password σου)

---

## 🧪 Δοκιμή του Backend API (χωρίς frontend)

Ελέγξε αν το Django λειτουργεί:

### Με curl:
```bash
# Health check
curl http://localhost:8000/accounting/api/health/

# Test endpoint
curl http://localhost:8000/accounting/api/test/
```

### Με browser:
Άνοιξε: `http://localhost:8000/accounting/api/health/`

Αν δεις JSON response, το backend δουλεύει σωστά!

---

## 🐛 Debug Steps

### 1. Έλεγξε αν το Django τρέχει:
```bash
curl http://localhost:8000/accounting/api/health/
```

**Αναμενόμενο:**
```json
{
  "status": "ok",
  "service": "LogistikoCRM",
  "timestamp": "..."
}
```

### 2. Έλεγξε το React developer console:

**Chrome DevTools:**
- F12 → Console tab
- Δες αν υπάρχουν άλλα errors εκτός του `ERR_BLOCKED_BY_CLIENT`

### 3. Έλεγξε το Network tab:

**Chrome DevTools:**
- F12 → Network tab
- Refresh τη σελίδα
- Πάτησε "Login"
- Δες το `/api/auth/login/` request:
  - **Blocked:** Ad blocker issue
  - **404:** URL λάθος
  - **500:** Backend error
  - **CORS error:** CORS issue

---

## 🔧 Εναλλακτικό: Χρήση του Django Admin Μόνο

Αν το React δεν λειτουργεί, μπορείς να χρησιμοποιήσεις το Django Admin:

```bash
python manage.py runserver 0.0.0.0:8000
```

Άνοιξε: `http://localhost:8000/admin/`

---

## 📞 Συχνές Ερωτήσεις

### Q: Γιατί βλέπω "Invalid HTTP_HOST header"?
**A:** Πρόσθεσε το IP στο `ALLOWED_HOSTS` στο `settings.py` (ήδη ρυθμισμένο για τοπικά δίκτυα).

### Q: Το React λέει "Failed to fetch"
**A:** Το Django backend δεν τρέχει. Εκκίνησέ το με `python manage.py runserver`.

### Q: Πώς βλέπω τι requests στέλνει το React;
**A:** F12 → Network tab → Refresh → Κάνε login → Δες το request `/api/auth/login/`

### Q: Μπορώ να αλλάξω το port του Django;
**A:** Ναι: `python manage.py runserver 0.0.0.0:9000`
Αλλά πρέπει να αλλάξεις και το `frontend/.env`:
```env
VITE_API_URL=http://localhost:9000/accounting
```

---

## 🚀 Production Setup (Μελλοντικά)

Για production χωρίς ad blocker issues:

1. **Χρησιμοποίησε domain name** (όχι localhost)
2. **HTTPS** με SSL certificate
3. **Nginx reverse proxy**
4. **DEBUG=False**

---

## 📝 Checklist

Πριν κάνεις login, βεβαιώσου:

- [ ] Django server τρέχει στο `http://localhost:8000`
- [ ] React dev server τρέχει (Vite)
- [ ] `.env` υπάρχει με `DEBUG=True`
- [ ] Ad blockers απενεργοποιημένα ή σε whitelist
- [ ] Browser console δεν δείχνει CORS errors
- [ ] Μπορείς να δεις: `http://localhost:8000/accounting/api/health/`

---

**Τελευταία Ενημέρωση:** Δεκέμβριος 2025
**Βοήθεια:** Αν εξακολουθείς να έχεις πρόβλημα, έλεγξε το Django log για errors.

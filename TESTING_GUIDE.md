# MediGuard Authentication - Quick Testing Guide

## Prerequisites
- Python 3.8+
- Flask installed
- SQLite (included with Python)
- Modern web browser

## Quick Start

### 1. Install Dependencies
```bash
cd c:\Users\Sai\ kumar\OneDrive\Desktop\MediGuard
pip install flask flask-sqlalchemy flask-cors werkzeug pandas scikit-learn joblib
```

### 2. Start the Server
```bash
python src/app.py
```

You should see:
```
* Running on http://localhost:5000
* Press CTRL+C to quit
```

### 3. Test in Browser
Open: **http://localhost:5000**

---

## Step-by-Step Testing

### Test 1: User Registration

**Steps:**
1. Click "Register" button or go to http://localhost:5000/register
2. Fill in form:
   - Email: `testuser@example.com`
   - Username: `testuser`
   - Password: `password123`
   - Age: `30`
   - Conditions: `Diabetes` (optional)
   - Allergies: `Penicillin` (optional)
3. Check box for Terms & Privacy Policy
4. Click "Create your account"

**Expected Result:**
- ✅ Success message appears: "✓ Account created! Redirecting to login..."
- ✅ After 2 seconds, redirects to login page
- ✅ Database file `mediguard.db` is created in project root

**If Error:**
- "Email already registered" → Email already exists (try different email)
- "Username must be at least 3 characters" → Username too short
- "Password must be at least 8 characters" → Password too short

---

### Test 2: User Login

**Steps:**
1. On login page, enter:
   - Email: `testuser@example.com`
   - Password: `password123`
2. Click "Sign in"

**Expected Result:**
- ✅ Success message: "✓ Login successful! Redirecting..."
- ✅ After 1.5 seconds, redirects to dashboard
- ✅ Navbar shows "Welcome, testuser!"
- ✅ Logout button appears next to username

**If Error:**
- "Invalid email or password" → Check email/password are correct
- Still on login page after click → Check browser console for errors (F12)

---

### Test 3: Dashboard Assessment

**Steps:**
1. After logging in, you should be on dashboard
2. Fill medication safety form:
   - Drug 1: `Warfarin`
   - Drug 2: `Aspirin`
   - Condition: `Hypertension`
3. Click "Assess Risk"

**Expected Result:**
- ✅ Loading message appears: "🔄 Analyzing medication interactions..."
- ✅ After 2-3 seconds, results display with risk colors
- ✅ Shows: DDI Risk, DFI Risk, DCI Risk, Overall Risk
- ✅ Recommendation appears based on risk level
- ✅ Assessment automatically saved to database

**Risk Levels You Might See:**
- 🔴 **High Risk** - Red background (requires doctor consultation)
- 🟠 **Moderate Risk** - Orange background (use with caution)
- 🟡 **Low Risk** - Yellow background (monitor side effects)
- 🟢 **Safe** - Green background (no interaction)

---

### Test 4: Assessment History

**Steps:**
1. Make several assessments with different drugs
2. Try different combinations:
   - Aspirin + Ibuprofen (High DDI risk)
   - Metformin + Lisinopril (Low risk)
   - Warfarin + Vitamin K (High DCI risk)

**Expected Result:**
- ✅ Each assessment shows in real-time
- ✅ Each assessment saved to database
- ✅ Can view assessment history (after we add history page)

**How to Verify Saved:**
Use SQLite command line:
```bash
sqlite3 mediguard.db
SELECT * FROM assessment_history;
.exit
```

---

### Test 5: User Logout

**Steps:**
1. On dashboard, click "Logout" button
2. Confirm redirect to login page

**Expected Result:**
- ✅ Session cleared
- ✅ localStorage cleared
- ✅ Redirected to login page
- ✅ Cannot access dashboard without logging in again

**If Error:**
- Still on dashboard after logout → Check browser console
- Unable to log back in → Try different email/check if user exists

---

### Test 6: Page Reload While Logged In

**Steps:**
1. After logging in, reload the page (F5 or Ctrl+R)

**Expected Result:**
- ✅ Still logged in (session restored)
- ✅ Username still shows in navbar
- ✅ Assessment form still visible

---

### Test 7: Access Dashboard Without Login

**Steps:**
1. In new incognito/private browser window
2. Go to http://localhost:5000/

**Expected Result:**
- ✅ Shows login prompt instead of assessment form
- ✅ Message: "🔒 Authentication Required"
- ✅ Shows "Log In / Register" link
- ✅ Cannot assess medications without logging in

---

## Database Verification

### Check User Created
```bash
sqlite3 mediguard.db
SELECT id, email, username, age, created_at FROM user;
```

### Check Assessment Saved
```bash
sqlite3 mediguard.db
SELECT drug1, drug2, condition, overall_risk, created_at FROM assessment_history ORDER BY created_at DESC;
```

### Check User Sessions (Flask stores in memory)
Sessions are stored in Flask memory, not database. To verify:
1. Open browser DevTools (F12)
2. Go to Storage → Cookies
3. Look for session cookie (named `session`)
4. Value should be a long encrypted string

---

## Common Test Cases

### Test Case 1: Register Multiple Users
**Users:**
- alice@example.com / alice_smith / password123
- bob@example.com / bob_jones / password123
- carol@example.com / carol_white / password123

**Expected:** Each can register and log in independently

---

### Test Case 2: Duplicate Email Prevention
**Steps:**
1. Register: john@example.com
2. Try to register same email again

**Expected:** "Email already registered" error

---

### Test Case 3: Weak Password Validation
**Steps:**
1. Try registering with password: `pass`
2. Try registering with password: `short`

**Expected:** "Password must be at least 8 characters" error

---

### Test Case 4: Concurrent Users
**Steps:**
1. Open two browser windows
2. Log in as different users in each
3. Make assessments in each

**Expected:** 
- ✅ Each user sees their own username
- ✅ Each user's assessments saved separately
- ✅ No cross-contamination

---

## Browser Console Checks

Open DevTools (F12) → Console tab to see:
- ✅ Login/Logout messages
- ✅ API call responses
- ✅ Assessment results
- ✅ Any JavaScript errors

**Expected console logs:**
```
✓ Assessment saved to history
{user: {id: 1, email: "test@example.com", username: "testuser"}}
POST /api/login HTTP/1.1 200
GET /api/user HTTP/1.1 200
POST /api/assessments HTTP/1.1 200
```

---

## Network Tab Checks

Open DevTools (F12) → Network tab to verify:

**Login request:**
- POST `/api/login`
- Status: 200
- Response body: `{user: {...}}`
- Response headers: `Set-Cookie: session=...`

**Assessment save request:**
- POST `/api/assessments`
- Status: 200
- Body: drug1, drug2, condition, risk levels

**Get user request:**
- GET `/api/user`
- Status: 200 (if logged in)
- Status: 401 (if not logged in)

---

## Troubleshooting Tests

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Run pip install
```bash
pip install flask flask-sqlalchemy flask-cors
```

### Issue: "Address already in use" on port 5000
**Solution:** 
```bash
# Find process on port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

Then restart Flask

### Issue: Database locked error
**Solution:** Close all SQLite connections
```bash
# This will reset database (loses all data)
del mediguard.db
python src/app.py
```

### Issue: "TemplateNotFound: login.html"
**Solution:** Make sure frontend folder is in correct location:
```
c:\Users\Sai kumar\OneDrive\Desktop\MediGuard\
├── frontend/
│   ├── login.html ✓
│   ├── register.html ✓
│   ├── dashboard.html ✓
│   ├── auth.js ✓
│   └── ...
├── src/
│   ├── app.py ✓
│   ├── auth.py ✓
│   ├── models.py ✓
│   └── ...
```

### Issue: CSS/JavaScript not loading (404 errors)
**Solution:** Make sure `frontend` folder is named correctly and files exist:
```bash
dir frontend
```

Should show: `auth.js`, `Login.html`, `register.html`, `dashboard.html`, `mediguard-api.js`, `Logo.png`

---

## Test Results Checklist

After running all tests, verify:

- [ ] User can register successfully
- [ ] Email/username uniqueness enforced
- [ ] Password strength validated (8+ chars)
- [ ] User can log in with correct credentials
- [ ] Username displays in navbar after login
- [ ] User can make assessments
- [ ] Assessment results display with risk colors
- [ ] Assessments saved to database
- [ ] User can log out
- [ ] Cannot access dashboard without login
- [ ] Multiple users work independently
- [ ] Session persists on page reload
- [ ] Session clears on logout
- [ ] Weak passwords rejected
- [ ] Duplicate emails rejected
- [ ] UI is responsive and user-friendly

---

## Performance Notes

- **Registration:** ~100ms (includes hashing + DB save)
- **Login:** ~150ms (includes hash verification)
- **Assessment:** ~200-500ms (depends on data processing)
- **Full page load:** ~1-2 seconds
- **Database queries:** <50ms on fresh database

---

## Support

If tests fail, check:
1. **Console errors** - F12 → Console tab
2. **Network requests** - F12 → Network tab
3. **Database** - `sqlite3 mediguard.db`
4. **Flask logs** - Terminal output from `python src/app.py`

---

**Ready to test? Start with Test 1: User Registration!** 🚀

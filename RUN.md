# How to Run the Student Enrollment App

## Quick Start Guide

You need **2 terminal windows** - one for the backend (Flask) and one for the frontend (React).

---

## Terminal 1: Backend (Flask)

1. **Open a terminal in the project root** (`cse108-lab08/`)

2. **Create and activate a virtual environment** (first time only):
```bash
python3 -m venv venv
source venv/bin/activate
```
   - On **Windows**: `venv\Scripts\activate`
   - On **macOS/Linux**: `source venv/bin/activate`

3. **Install Python dependencies** (first time only):
```bash
pip install -r requirements.txt
```

4. **Run the Flask server**:
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

✅ **Backend is now running on `http://localhost:5000`**

---

## Terminal 2: Frontend (React)

1. **Open a NEW terminal window** and navigate to the client folder:
```bash
cd client
```

2. **Install Node dependencies** (first time only):
```bash
npm install
```

3. **Run the React development server**:
```bash
npm run dev
```

You should see:
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

✅ **Frontend is now running on `http://localhost:5173`**

---

## Access the Application

1. **Open your browser** and go to: `http://localhost:5173`

2. **Login as Admin** (default account):
   - Username: `admin`
   - Password: `admin123`

3. **To access Flask-Admin** (after logging in as admin):
   - Open: `http://localhost:5000/admin`

---

## Testing the Application

### Step 1: Create Test Users (via Flask-Admin)

1. Login as admin at `http://localhost:5173`
2. Click the "Open Admin Panel" link, or go directly to `http://localhost:5000/admin`
3. Click "Users" → "Create"
4. Create test users:
   - **Student**: username=`student1`, password=`test123`, role=`student`, first_name=`John`, last_name=`Doe`
   - **Teacher**: username=`teacher1`, password=`test123`, role=`teacher`, first_name=`Jane`, last_name=`Smith`

### Step 2: Create Classes (via Flask-Admin)

1. In Flask-Admin, click "Classes" → "Create"
2. Create a class:
   - Course Code: `CSE 162`
   - Name: `Introduction to Programming`
   - Description: `Learn the basics of programming`
   - Teacher: Select the teacher you created
   - Capacity: `30`

### Step 3: Test Student Features

1. Logout as admin
2. Login as `student1` / `test123`
3. You should see:
   - Welcome message
   - "Your Courses" section (empty initially)
   - "Available Courses" section with the class you created
   - Click "Enroll" to enroll in a class

### Step 4: Test Teacher Features

1. Logout as student
2. Login as `teacher1` / `test123`
3. You should see:
   - Welcome message with "Dr. Smith"
   - "Your Courses" section with the class you created
   - Click on the course to see enrolled students
   - Edit grades for students

---

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**"Port 5000 already in use":**
- Stop other Flask apps or change the port in `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Change to 5001
  ```
- Also update `client/vite.config.ts` to use port 5001

**Database errors:**
- Delete `university.db` and restart the Flask app to recreate the database

### Frontend Issues

**"Cannot find module" errors:**
```bash
cd client
npm install
```

**"Port 5173 already in use":**
- Vite will automatically use the next available port (5174, 5175, etc.)
- Check the terminal output for the actual port

**CORS errors:**
- Make sure the Flask server is running
- Check that `client/vite.config.ts` has the proxy configured correctly

### General Issues

**Backend and Frontend won't connect:**
1. Make sure both servers are running
2. Backend should be on port 5000
3. Frontend should be on port 5173 (or as shown in terminal)
4. The frontend proxy should forward `/api` requests to `http://localhost:5000`

---

## Quick Commands Reference

### Backend (Terminal 1)
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Run server
python app.py
```

### Frontend (Terminal 2)
```bash
cd client
npm run dev
```

---

## What to Expect

✅ **Working correctly if you see:**
- Backend: `Running on http://127.0.0.1:5000`
- Frontend: `Local: http://localhost:5173/`
- Login page loads at `http://localhost:5173`
- Can login with admin credentials
- Admin panel accessible at `http://localhost:5000/admin`

🚨 **Something is wrong if:**
- Browser shows "Cannot connect" or "Network error"
- Login fails immediately
- 404 errors in browser console
- Backend shows connection refused errors

---

## Next Steps After Setup

1. ✅ Create test users via Flask-Admin
2. ✅ Create classes via Flask-Admin
3. ✅ Test student enrollment
4. ✅ Test teacher grade editing
5. ✅ Test admin CRUD operations

For more details, see `SETUP.md` or `README.md`.


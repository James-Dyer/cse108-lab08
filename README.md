# CSE 108 Lab 08: Student Enrollment Web App

A full-stack Student Enrollment Web Application for ACME University with three user roles: **Student**, **Teacher**, and **Admin**.

## Features

### Student Features
- ✅ Login/Logout
- ✅ View enrolled courses
- ✅ Browse all courses offered
- ✅ View course details (instructor, enrollment count, capacity)
- ✅ Enroll in courses (with capacity validation)
- ✅ View grades

### Teacher Features
- ✅ Login/Logout
- ✅ View courses they teach
- ✅ View enrolled students for each course
- ✅ Edit student grades inline

### Admin Features
- ✅ Login/Logout
- ✅ Full CRUD operations via Flask-Admin
- ✅ Manage users, classes, enrollments
- ✅ Edit all data in the system

## Tech Stack

**Backend:**
- Flask (Python web framework)
- Flask-Admin (admin interface)
- SQLAlchemy (ORM)
- SQLite (database)
- Flask-CORS (cross-origin support)

**Frontend:**
- React 19
- TypeScript
- Vite
- Axios (HTTP client)

## Quick Start

### Backend Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python app.py
```

The server runs on `http://localhost:5000`
Flask-Admin interface: `http://localhost:5000/admin`

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

The app runs on `http://localhost:5173`

## Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`

Use the Flask-Admin interface to create users and classes.

## Project Structure

```
cse108-lab08/
├── app.py                 # Flask application and API routes
├── models.py              # Database models (User, Class, Enrollment)
├── requirements.txt       # Python dependencies
├── SETUP.md              # Detailed setup instructions
├── README.md             # This file
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # React components (Login, Dashboards)
│   │   ├── api.ts        # API client
│   │   └── App.tsx       # Main app component
│   └── package.json      # Node dependencies
└── university.db         # SQLite database (created automatically)
```

## API Documentation

See `SETUP.md` for detailed API endpoint documentation.

## Validation Rules

1. **Enrollment Validation**:
   - Students cannot enroll in classes at capacity
   - Students cannot enroll in the same class twice

2. **Grade Editing**:
   - Only teachers can edit grades
   - Teachers can only edit grades for their own classes
   - Grades must be between 0-100 or null

3. **Role-Based Access Control**:
   - Students can only access student routes
   - Teachers can only access teacher routes
   - Admins have full access via Flask-Admin

## License

This project is for educational purposes (CSE 108 Lab 08).

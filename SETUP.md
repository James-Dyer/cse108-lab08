# Student Enrollment Web App - Setup Instructions

## Overview
A full-stack Student Enrollment Web Application with three user roles: Student, Teacher, and Admin.

## Prerequisites
- Python 3.8+
- Node.js 18+ and npm
- Virtual environment (recommended)

## Backend Setup (Flask)

1. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize the database**:
The database will be created automatically when you first run the Flask app. A default admin user will be created:
- Username: `admin`
- Password: `admin123`

4. **Run the Flask server**:
```bash
python app.py
```

The Flask server will run on `http://localhost:5000`

The Flask-Admin interface will be available at `http://localhost:5000/admin`

## Frontend Setup (React)

1. **Navigate to the client directory**:
```bash
cd client
```

2. **Install dependencies**:
```bash
npm install
```

3. **Run the development server**:
```bash
npm run dev
```

The React app will run on `http://localhost:5173` (or another port if 5173 is occupied)

## Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin

You can use the Flask-Admin interface at `http://localhost:5000/admin` to:
- Create users (students, teachers, admins)
- Create classes
- Manage enrollments
- Edit grades

## Creating Test Users

### Using Flask-Admin:
1. Log in as admin
2. Go to `http://localhost:5000/admin`
3. Click on "Users" → "Create"
4. Fill in user details:
   - Username
   - Password (will be hashed automatically)
   - Role (student, teacher, or admin)
   - First name, Last name
   - Email (optional)

### Using Python console:
```python
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create a student
    student = User(
        username='student1',
        password=generate_password_hash('password123'),
        role='student',
        first_name='John',
        last_name='Doe',
        email='student1@acme.edu'
    )
    db.session.add(student)
    
    # Create a teacher
    teacher = User(
        username='teacher1',
        password=generate_password_hash('password123'),
        role='teacher',
        first_name='Jane',
        last_name='Smith',
        email='teacher1@acme.edu'
    )
    db.session.add(teacher)
    db.session.commit()
```

## API Endpoints

### Authentication
- `POST /api/login` - Login
- `POST /api/logout` - Logout
- `GET /api/check-auth` - Check authentication status

### Student Routes
- `GET /api/student/dashboard` - Get student dashboard data
- `GET /api/student/courses` - Get all courses
- `POST /api/student/enroll/<class_id>` - Enroll in a class

### Teacher Routes
- `GET /api/teacher/dashboard` - Get teacher dashboard data
- `GET /api/teacher/course/<class_id>` - Get course details with students
- `PUT /api/teacher/grade/<enrollment_id>` - Update student grade

### Admin
- Access Flask-Admin at `/admin`

## Features

### Student Features
- ✅ Login/Logout
- ✅ View enrolled courses
- ✅ Browse all courses
- ✅ View course details (instructor, enrollment, capacity)
- ✅ Enroll in courses (with validation)
- ✅ View grades

### Teacher Features
- ✅ Login/Logout
- ✅ View courses they teach
- ✅ View enrolled students for each course
- ✅ Edit student grades

### Admin Features
- ✅ Login/Logout
- ✅ Full CRUD operations via Flask-Admin
- ✅ Manage users, classes, enrollments
- ✅ Edit all data in the system

## Validation Rules

1. **Enrollment Validation**:
   - Students cannot enroll in a class that's at capacity
   - Students cannot enroll in the same class twice
   - Enrollment is only allowed for students

2. **Grade Editing**:
   - Only teachers can edit grades
   - Teachers can only edit grades for classes they teach
   - Grades must be between 0 and 100 (or null)

3. **Role-Based Access Control**:
   - Students can only access student routes
   - Teachers can only access teacher routes
   - Admins have full access via Flask-Admin

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password` (Hashed)
- `role` (student/teacher/admin)
- `first_name`, `last_name`
- `email` (Optional)

### Classes Table
- `id` (Primary Key)
- `course_code` (Unique, e.g., "CSE 162")
- `name`
- `description`
- `teacher_id` (Foreign Key → Users)
- `capacity`

### Enrollments Table
- `id` (Primary Key)
- `student_id` (Foreign Key → Users)
- `class_id` (Foreign Key → Classes)
- `grade` (Nullable Float)
- Unique constraint on (student_id, class_id)

## Troubleshooting

1. **Port conflicts**: If port 5000 or 5173 is in use, change them in the respective config files.

2. **Database issues**: Delete `university.db` and restart the Flask app to recreate the database.

3. **CORS errors**: Make sure Flask-CORS is installed and the frontend proxy is configured correctly.

4. **Session issues**: Ensure cookies are enabled in your browser for `localhost`.

## Project Structure

```
cse108-lab08/
├── app.py                 # Flask application and routes
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── SETUP.md              # This file
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── api.ts        # API client
│   │   ├── App.tsx       # Main app component
│   │   └── ...
│   └── package.json      # Node dependencies
└── university.db         # SQLite database (created on first run)
```


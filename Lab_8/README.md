# Student Enrollment Web Application

A Flask-based web application for managing student enrollment, course assignments, and grades with role-based access control.

## Features

- **Three User Roles:**
  - **Student**: View enrolled courses, browse available courses, enroll in courses (with capacity checking)
  - **Teacher**: View teaching assignments, manage student grades for assigned courses
  - **Admin**: Full CRUD access via Flask-Admin panel for all database entities

- **Authentication System**: Secure login/logout with session management and role-based access control

- **Database Models:**
  - Users (Students, Teachers, Admins)
  - Courses (with capacity tracking)
  - Enrollments (linking students to courses)
  - Grades (linked to enrollments)
  - Teacher-Course assignments

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

## Demo Accounts

- **Admin:**
  - Username: `admin`
  - Password: `admin123`

- **Teacher:**
  - Username: `teacher1`
  - Password: `teacher123`

- **Student:**
  - Username: `student1`
  - Password: `student123`
  - Username: `student2`
  - Password: `student123`

## Routes

### Authentication
- `/login` - Login page for all users
- `/logout` - Logout (redirects to login)

### Student Routes
- `/student/courses` - View enrolled courses
- `/student/add` - Browse and enroll in available courses

### Teacher Routes
- `/teacher/courses` - View assigned courses
- `/teacher/course/<id>` - View students and manage grades for a specific course

### Admin Routes
- `/admin` - Flask-Admin panel for CRUD operations on all entities

## Database

The application uses SQLite database stored in the `instance/` folder. The database is automatically initialized with sample data on first run.

## Project Structure

```
Lab_8/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── student_courses.html
│   ├── student_add.html
│   ├── teacher_courses.html
│   └── teacher_course_detail.html
├── static/            # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── instance/          # Database files (created automatically)
    └── enrollment.db
```

## Security Notes

- Passwords are hashed using Werkzeug's password hashing
- Sessions are used for authentication
- Role-based access control ensures users can only access appropriate routes
- Flask-Admin is protected and only accessible to admin users

## Requirements Met

✅ Three distinct user roles (Student, Teacher, Admin)
✅ Role-based authentication with session management
✅ Student enrollment with capacity checking
✅ Teacher grade management for assigned courses
✅ Flask-Admin panel for full CRUD operations
✅ All required routes implemented
✅ Proper error handling and user feedback

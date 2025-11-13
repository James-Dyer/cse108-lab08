# Lab 8: Student Enrollment Web App — Machine-Readable Instructions

This document converts the provided lab instructions into structured, machine-readable requirements suitable for an AI agent to execute.

---

## PROJECT OVERVIEW
**Title:** Student Enrollment Web Application  
**Points:** 300 (equivalent to 3 labs)  
**Team Size:** 3–4 people  
**Timeline:** 3 weeks  
**Deliverable:** Group presentation during lab session

---

## CORE USER ROLES
The application supports **three distinct roles**: Student, Teacher, and Admin.

### 1. Student User Capabilities
**Role ID:** `student`

**User Stories:**
- `student.login`: User can log in and log out.
- `student.view_my_classes`: User can view all classes they are enrolled in.
- `student.view_all_classes`: User can view all classes offered by the university.
- `student.view_class_size`: User can see the number of students enrolled in a given class.
- `student.enroll`: User can sign up for a class *only if* the class capacity has not been reached.

**Constraints:**
- Enrollment should fail with an error if the class is full.

---

### 2. Teacher User Capabilities
**Role ID:** `teacher`

**User Stories:**
- `teacher.login`: User can log in and log out.
- `teacher.view_my_classes`: User can view all classes they teach.
- `teacher.view_students`: User can view all students enrolled in each class they teach.
- `teacher.view_grades`: User can see grades for students in each class.
- `teacher.edit_grade`: User can update/edit a student’s grade.

**Constraints:**
- Grade editing allowed only for classes taught by the authenticated teacher.

---

### 3. Admin User Capabilities
**Role ID:** `admin`

**User Stories:**
- `admin.crud`: Admin can **create**, **read**, **update**, and **delete** all data in the database.
- `admin.panel`: Admin interface must be implemented using **Flask-Admin**.

**Entities Admin Can Modify:**
- Students
- Teachers
- Courses
- Enrollments
- Grades

---

## SYSTEM REQUIREMENTS

### Authentication
- Must support **role-based login**: Student, Teacher, Admin.
- Sessions should persist during usage and invalidate on logout.

### Data Model (Suggested)
```
User(id, username, password_hash, role)
Course(id, name, department, capacity)
Enrollment(id, user_id, course_id)
Grade(id, enrollment_id, grade_value)
```

### Application Pages
| Page | Description | Roles |
|------|-------------|-------|
| `/login` | Log in | all |
| `/logout` | Log out | all |
| `/student/courses` | Shows student's enrolled courses | student |
| `/student/add` | Displays all available courses | student |
| `/teacher/courses` | Shows courses taught by teacher | teacher |
| `/teacher/course/<id>` | Shows students + grades | teacher |
| `/admin` | Flask-Admin panel | admin |

---

## ACCEPTANCE CRITERIA (HIGH-LEVEL)
### Student
- Able to view only their classes.
- Cannot enroll in full courses.
- Sees accurate class sizes.

### Teacher
- Can only see classes they teach.
- Can modify grades for students in those classes.

### Admin
- Full CRUD across all tables via Flask-Admin interface.

---






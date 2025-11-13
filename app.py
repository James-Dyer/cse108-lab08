from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Class, Enrollment
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///university.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
db.init_app(app)

# Initialize Flask-Admin
admin = Admin(app, name='ACME University Admin', template_mode='bootstrap3')

# Custom Admin Views with role-based access
class SecureModelView(ModelView):
    """Base ModelView with authentication check"""
    def is_accessible(self):
        if 'user_id' not in session:
            return False
        user = User.query.get(session['user_id'])
        return user and user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        # Redirect to main app login page
        return redirect('/')

class UserAdminView(SecureModelView):
    column_list = ['id', 'username', 'role', 'first_name', 'last_name', 'email']
    form_columns = ['username', 'password', 'role', 'first_name', 'last_name', 'email']
    
    def on_model_change(self, form, model, is_created):
        if is_created or 'password' in form.data:
            if form.data.get('password'):
                model.password = generate_password_hash(form.data['password'])

class ClassAdminView(SecureModelView):
    # Use the foreign-key field `teacher_id` to avoid mapper issues with
    # the backref relationship name in Flask-Admin.
    column_list = ['id', 'course_code', 'name', 'teacher_id', 'capacity']
    form_columns = ['course_code', 'name', 'description', 'teacher_id', 'capacity']

class EnrollmentAdminView(SecureModelView):
    # Use the foreign-key fields directly for simplicity.
    column_list = ['id', 'student_id', 'class_id', 'grade']
    form_columns = ['student_id', 'class_id', 'grade']

# Register admin views
admin.add_view(UserAdminView(User, db.session))
admin.add_view(ClassAdminView(Class, db.session))
admin.add_view(EnrollmentAdminView(Enrollment, db.session))

# Role-based decorator
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            user = User.query.get(session['user_id'])
            if not user or user.role != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Root route - API information
@app.route('/')
def index():
    return jsonify({
        'message': 'ACME University Student Enrollment API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'login': 'POST /api/login',
                'logout': 'POST /api/logout',
                'check_auth': 'GET /api/check-auth'
            },
            'student': {
                'dashboard': 'GET /api/student/dashboard',
                'courses': 'GET /api/student/courses',
                'enroll': 'POST /api/student/enroll/<class_id>'
            },
            'teacher': {
                'dashboard': 'GET /api/teacher/dashboard',
                'course_detail': 'GET /api/teacher/course/<class_id>',
                'update_grade': 'PUT /api/teacher/grade/<enrollment_id>'
            },
            'admin': {
                'flask_admin': 'GET /admin (requires admin login)'
            }
        },
        'frontend': 'The React frontend should be running on http://localhost:5173',
        'admin_panel': 'Admin panel available at http://localhost:5000/admin (requires admin login)'
    }), 200

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }), 200
    return jsonify({'authenticated': False}), 200

# Student routes
@app.route('/api/student/dashboard', methods=['GET'])
@role_required('student')
def student_dashboard():
    user = User.query.get(session['user_id'])
    enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    
    enrolled_classes = []
    for enrollment in enrollments:
        class_data = enrollment.class_obj
        enrolled_classes.append({
            'id': class_data.id,
            'course_code': class_data.course_code,
            'name': class_data.name,
            'description': class_data.description,
            'instructor': f"{class_data.teacher.first_name} {class_data.teacher.last_name}",
            'capacity': class_data.capacity,
            'current_enrollment': class_data.current_enrollment,
            'grade': enrollment.grade
        })
    
    return jsonify({
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'enrolled_courses': enrolled_classes
    }), 200

@app.route('/api/student/courses', methods=['GET'])
@role_required('student')
def student_all_courses():
    user = User.query.get(session['user_id'])
    all_classes = Class.query.all()
    
    courses = []
    for class_obj in all_classes:
        enrollment = Enrollment.query.filter_by(
            student_id=user.id,
            class_id=class_obj.id
        ).first()
        
        courses.append({
            'id': class_obj.id,
            'course_code': class_obj.course_code,
            'name': class_obj.name,
            'description': class_obj.description,
            'instructor': f"{class_obj.teacher.first_name} {class_obj.teacher.last_name}",
            'capacity': class_obj.capacity,
            'current_enrollment': class_obj.current_enrollment,
            'is_enrolled': enrollment is not None,
            'grade': enrollment.grade if enrollment else None
        })
    
    return jsonify({'courses': courses}), 200

@app.route('/api/student/enroll/<int:class_id>', methods=['POST'])
@role_required('student')
def enroll_in_class(class_id):
    user = User.query.get(session['user_id'])
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=user.id,
        class_id=class_id
    ).first()
    if existing:
        return jsonify({'error': 'Already enrolled in this class'}), 400
    
    # Check capacity
    if class_obj.current_enrollment >= class_obj.capacity:
        return jsonify({'error': 'Class is at full capacity'}), 400
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=user.id,
        class_id=class_id,
        grade=None
    )
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Successfully enrolled in class'}), 200

# Teacher routes
@app.route('/api/teacher/dashboard', methods=['GET'])
@role_required('teacher')
def teacher_dashboard():
    user = User.query.get(session['user_id'])
    classes = Class.query.filter_by(teacher_id=user.id).all()
    
    courses = []
    for class_obj in classes:
        courses.append({
            'id': class_obj.id,
            'course_code': class_obj.course_code,
            'name': class_obj.name,
            'description': class_obj.description,
            'capacity': class_obj.capacity,
            'current_enrollment': class_obj.current_enrollment
        })
    
    return jsonify({
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'courses': courses
    }), 200

@app.route('/api/teacher/course/<int:class_id>', methods=['GET'])
@role_required('teacher')
def teacher_course_detail(class_id):
    user = User.query.get(session['user_id'])
    class_obj = Class.query.get_or_404(class_id)
    
    # Verify teacher owns this class
    if class_obj.teacher_id != user.id:
        return jsonify({'error': 'Not authorized to view this class'}), 403
    
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    
    students = []
    for enrollment in enrollments:
        student = enrollment.student
        students.append({
            'enrollment_id': enrollment.id,
            'student_id': student.id,
            'student_name': f"{student.first_name} {student.last_name}",
            'username': student.username,
            'grade': enrollment.grade
        })
    
    return jsonify({
        'course': {
            'id': class_obj.id,
            'course_code': class_obj.course_code,
            'name': class_obj.name,
            'description': class_obj.description
        },
        'students': students
    }), 200

@app.route('/api/teacher/grade/<int:enrollment_id>', methods=['PUT'])
@role_required('teacher')
def update_grade(enrollment_id):
    user = User.query.get(session['user_id'])
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Verify teacher owns this class
    if enrollment.class_obj.teacher_id != user.id:
        return jsonify({'error': 'Not authorized to edit grades for this class'}), 403
    
    data = request.get_json()
    grade = data.get('grade')
    
    # Validate grade (optional - could add more validation)
    if grade and (not isinstance(grade, (int, float)) or grade < 0 or grade > 100):
        return jsonify({'error': 'Invalid grade. Must be between 0 and 100'}), 400
    
    enrollment.grade = grade
    db.session.commit()
    
    return jsonify({
        'message': 'Grade updated successfully',
        'enrollment': {
            'id': enrollment.id,
            'student_id': enrollment.student_id,
            'grade': enrollment.grade
        }
    }), 200

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()

        # --- Admin user ---
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin',
                first_name='Admin',
                last_name='User',
                email='admin@acme.edu',
            )
            db.session.add(admin)
            db.session.commit()

        # --- Sample teachers ---
        teachers_data = [
            ('ralph', 'Ralph', 'Jenkins'),
            ('susan', 'Susan', 'Walker'),
            ('ammon', 'Ammon', 'Hepworth'),
        ]
        teachers = {}
        for username, first, last in teachers_data:
            teacher = User.query.filter_by(username=username).first()
            if not teacher:
                teacher = User(
                    username=username,
                    password=generate_password_hash('teacher123'),
                    role='teacher',
                    first_name=first,
                    last_name=last,
                    email=f'{username}@acme.edu',
                )
                db.session.add(teacher)
                db.session.flush()
            teachers[username] = teacher

        # --- Sample students ---
        students_data = [
            ('jose', 'Jose', 'Santos'),
            ('betty', 'Betty', 'Brown'),
            ('john', 'John', 'Stuart'),
            ('li', 'Li', 'Cheng'),
            ('nancy', 'Nancy', 'Little'),
            ('mindy', 'Mindy', 'Norris'),
            ('aditya', 'Aditya', 'Ranganath'),
            ('yiwen', 'Yi Wen', 'Chen'),
        ]
        students = {}
        for username, first, last in students_data:
            student = User.query.filter_by(username=username).first()
            if not student:
                student = User(
                    username=username,
                    password=generate_password_hash('student123'),
                    role='student',
                    first_name=first,
                    last_name=last,
                    email=f'{username}@acme.edu',
                )
                db.session.add(student)
                db.session.flush()
            students[username] = student

        # --- Sample classes / courses ---
        classes_definitions = [
            # course_code, name, description (time), teacher_username, capacity
            ('MATH 101', 'Math 101', 'MWF 10:00-10:50 AM', 'ralph', 8),
            ('PHYS 121', 'Physics 121', 'TR 11:00-11:50 AM', 'susan', 10),
            ('CS 106', 'CS 106', 'MWF 2:00-2:50 PM', 'ammon', 10),
            ('CS 162', 'CS 162', 'TR 3:00-3:50 PM', 'ammon', 4),
        ]
        classes = {}
        for code, name, desc, teacher_username, capacity in classes_definitions:
            course = Class.query.filter_by(course_code=code).first()
            if not course:
                teacher = teachers[teacher_username]
                course = Class(
                    course_code=code,
                    name=name,
                    description=desc,
                    teacher_id=teacher.id,
                    capacity=capacity,
                )
                db.session.add(course)
                db.session.flush()
            classes[code] = course

        # --- Sample enrollments with grades (from provided table) ---
        enrollments_data = [
            # course_code, student_username, grade
            ('MATH 101', 'jose', 92),
            ('MATH 101', 'betty', 65),
            ('MATH 101', 'john', 86),
            ('MATH 101', 'li', 77),
            ('PHYS 121', 'nancy', 53),
            ('PHYS 121', 'li', 85),
            ('PHYS 121', 'mindy', 94),
            ('PHYS 121', 'john', 91),
            ('PHYS 121', 'betty', 88),
            ('CS 106', 'aditya', 93),
            ('CS 106', 'yiwen', 85),
            ('CS 106', 'nancy', 57),
            ('CS 106', 'mindy', 68),
            ('CS 162', 'aditya', 99),
            ('CS 162', 'nancy', 87),
            ('CS 162', 'yiwen', 92),
            ('CS 162', 'john', 67),
        ]

        for course_code, student_username, grade in enrollments_data:
            course = classes.get(course_code)
            student = students.get(student_username)
            if not course or not student:
                continue
            existing = Enrollment.query.filter_by(
                student_id=student.id, class_id=course.id
            ).first()
            if not existing:
                enrollment = Enrollment(
                    student_id=student.id,
                    class_id=course.id,
                    grade=grade,
                )
                db.session.add(enrollment)

        db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)


"""
Flask Student Enrollment Web Application
This application provides role-based access for Students, Teachers, and Admins
with enrollment management, grade tracking, and administrative capabilities.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)
database_path = os.path.join(instance_path, 'enrollment.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ===== DATABASE MODELS =====

class User(db.Model):
    """User model for Students, Teachers, and Admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', or 'admin'
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True, cascade='all, delete-orphan')
    taught_courses = db.relationship('TeacherCourse', backref='teacher', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Course(db.Model):
    """Course model for university courses"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    teacher_courses = db.relationship('TeacherCourse', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def get_enrollment_count(self):
        """Get current number of enrolled students"""
        return len(self.enrollments)
    
    def is_full(self):
        """Check if course has reached capacity"""
        return self.get_enrollment_count() >= self.capacity
    
    def __repr__(self):
        return f'<Course {self.name} ({self.department})>'

class Enrollment(db.Model):
    """Enrollment model linking students to courses"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relationships
    grade = db.relationship('Grade', backref='enrollment', uselist=False, cascade='all, delete-orphan')
    
    # Ensure one enrollment per student per course
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),)
    
    def __repr__(self):
        return f'<Enrollment User {self.user_id} in Course {self.course_id}>'

class Grade(db.Model):
    """Grade model for student grades in courses"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False, unique=True)
    grade_value = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Grade {self.grade_value} for Enrollment {self.enrollment_id}>'

class TeacherCourse(db.Model):
    """Junction table linking teachers to courses they teach"""
    __tablename__ = 'teacher_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Ensure one record per teacher-course combination
    __table_args__ = (db.UniqueConstraint('teacher_id', 'course_id', name='unique_teacher_course'),)
    
    def __repr__(self):
        return f'<TeacherCourse Teacher {self.teacher_id} teaches Course {self.course_id}>'

# ===== FLASK-ADMIN CONFIGURATION =====

class SecureAdminIndexView(AdminIndexView):
    """Custom admin index view with authentication check"""
    def is_accessible(self):
        return session.get('logged_in') and session.get('role') == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('login'))
        elif session.get('role') != 'admin':
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('index'))
        return redirect(url_for('login'))

class SecureModelView(ModelView):
    """Custom model view with authentication check"""
    def is_accessible(self):
        return session.get('logged_in') and session.get('role') == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('login'))
        elif session.get('role') != 'admin':
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('index'))
        return redirect(url_for('login'))

class UserModelView(SecureModelView):
    """Custom view for User model"""
    column_list = ('id', 'username', 'role')
    column_searchable_list = ('username', 'role')
    form_columns = ('username', 'password_hash', 'role')
    column_labels = {'username': 'Username', 'role': 'Role', 'password_hash': 'Password Hash'}

class CourseModelView(SecureModelView):
    """Custom view for Course model"""
    column_list = ('id', 'name', 'department', 'capacity')
    column_searchable_list = ('name', 'department')
    form_columns = ('name', 'department', 'capacity')
    column_labels = {'name': 'Course Name', 'department': 'Department', 'capacity': 'Capacity'}

class EnrollmentModelView(SecureModelView):
    """Custom view for Enrollment model"""
    column_list = ('id', 'user_id', 'course_id', 'user', 'course')
    form_columns = ('user_id', 'course_id')
    column_labels = {'user_id': 'User ID', 'course_id': 'Course ID', 'user': 'Student', 'course': 'Course'}

class GradeModelView(SecureModelView):
    """Custom view for Grade model"""
    column_list = ('id', 'enrollment_id', 'grade_value', 'enrollment')
    form_columns = ('enrollment_id', 'grade_value')
    column_labels = {'enrollment_id': 'Enrollment ID', 'grade_value': 'Grade', 'enrollment': 'Enrollment'}

class TeacherCourseModelView(SecureModelView):
    """Custom view for TeacherCourse model"""
    column_list = ('id', 'teacher_id', 'course_id', 'teacher', 'course')
    form_columns = ('teacher_id', 'course_id')
    column_labels = {'teacher_id': 'Teacher ID', 'course_id': 'Course ID', 'teacher': 'Teacher', 'course': 'Course'}

# Initialize Flask-Admin
admin = Admin(app, name='Student Enrollment Admin', template_mode='bootstrap3', index_view=SecureAdminIndexView())

# Add admin views for all models with custom views
admin.add_view(UserModelView(User, db.session, name='Users', category='Data'))
admin.add_view(CourseModelView(Course, db.session, name='Courses', category='Data'))
admin.add_view(EnrollmentModelView(Enrollment, db.session, name='Enrollments', category='Data'))
admin.add_view(GradeModelView(Grade, db.session, name='Grades', category='Data'))
admin.add_view(TeacherCourseModelView(TeacherCourse, db.session, name='Teacher Courses', category='Data'))

# Add logout link to admin menu
class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return session.get('logged_in') and session.get('role') == 'admin'

admin.add_link(LogoutMenuLink(name='Logout', category='', url='/logout'))
admin.add_link(LogoutMenuLink(name='Home', category='', url='/'))

# ===== AUTHENTICATION DECORATORS =====

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ===== ROUTE HANDLERS =====

# ===== ERROR HANDLERS =====

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    elif session.get('role') != 'admin' and request.path.startswith('/admin'):
        flash('You do not have permission to access the admin panel.', 'danger')
        return redirect(url_for('index'))
    flash('You do not have permission to access this page.', 'danger')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Home page - redirects based on role"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    role = session.get('role')
    if role == 'student':
        return redirect(url_for('student_courses'))
    elif role == 'teacher':
        return redirect(url_for('teacher_courses'))
    elif role == 'admin':
        return redirect(url_for('admin.index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for all users"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route for all users"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ===== STUDENT ROUTES =====

@app.route('/student/courses')
@login_required
@role_required('student')
def student_courses():
    """Display all courses the student is enrolled in"""
    user_id = session.get('user_id')
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    courses_data = []
    for enrollment in enrollments:
        course = enrollment.course
        grade = enrollment.grade
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'department': course.department,
            'capacity': course.capacity,
            'enrolled': course.get_enrollment_count(),
            'grade': grade.grade_value if grade else None
        })
    
    return render_template('student_courses.html', courses=courses_data)

@app.route('/student/add')
@login_required
@role_required('student')
def student_add():
    """Display all available courses for enrollment"""
    user_id = session.get('user_id')
    
    # Get all courses
    all_courses = Course.query.all()
    
    # Get courses the student is already enrolled in
    enrolled_course_ids = {e.course_id for e in Enrollment.query.filter_by(user_id=user_id).all()}
    
    courses_data = []
    for course in all_courses:
        is_enrolled = course.id in enrolled_course_ids
        enrollment_count = course.get_enrollment_count()
        is_full = course.is_full()
        
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'department': course.department,
            'capacity': course.capacity,
            'enrolled': enrollment_count,
            'available': course.capacity - enrollment_count,
            'is_enrolled': is_enrolled,
            'is_full': is_full
        })
    
    return render_template('student_add.html', courses=courses_data)

@app.route('/student/enroll/<int:course_id>', methods=['POST'])
@login_required
@role_required('student')
def student_enroll(course_id):
    """Enroll student in a course"""
    user_id = session.get('user_id')
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'warning')
        return redirect(url_for('student_add'))
    
    # Check if course is full
    if course.is_full():
        flash(f'Cannot enroll: {course.name} is full ({course.get_enrollment_count()}/{course.capacity}).', 'danger')
        return redirect(url_for('student_add'))
    
    # Create enrollment
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.name}!', 'success')
    return redirect(url_for('student_courses'))

@app.route('/student/drop/<int:course_id>', methods=['POST'])
@login_required
@role_required('student')
def student_drop(course_id):
    """Drop a course"""
    user_id = session.get('user_id')
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if enrollment:
        course_name = enrollment.course.name
        db.session.delete(enrollment)
        db.session.commit()
        flash(f'Successfully dropped {course_name}.', 'success')
    else:
        flash('Enrollment not found.', 'danger')
    
    return redirect(url_for('student_courses'))

# ===== TEACHER ROUTES =====

@app.route('/teacher/courses')
@login_required
@role_required('teacher')
def teacher_courses():
    """Display all courses the teacher teaches"""
    teacher_id = session.get('user_id')
    teacher_courses_rel = TeacherCourse.query.filter_by(teacher_id=teacher_id).all()
    
    courses_data = []
    for tc in teacher_courses_rel:
        course = tc.course
        enrollment_count = course.get_enrollment_count()
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'department': course.department,
            'capacity': course.capacity,
            'enrolled': enrollment_count
        })
    
    return render_template('teacher_courses.html', courses=courses_data)

@app.route('/teacher/course/<int:course_id>')
@login_required
@role_required('teacher')
def teacher_course_detail(course_id):
    """Display students and grades for a specific course"""
    teacher_id = session.get('user_id')
    
    # Verify teacher teaches this course
    teacher_course = TeacherCourse.query.filter_by(teacher_id=teacher_id, course_id=course_id).first()
    if not teacher_course:
        flash('You do not teach this course.', 'danger')
        return redirect(url_for('teacher_courses'))
    
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    students_data = []
    for enrollment in enrollments:
        student = enrollment.user
        grade = enrollment.grade
        students_data.append({
            'enrollment_id': enrollment.id,
            'student_id': student.id,
            'student_name': student.username,
            'grade': grade.grade_value if grade else None,
            'grade_id': grade.id if grade else None
        })
    
    return render_template('teacher_course_detail.html', course=course, students=students_data)

@app.route('/teacher/grade/<int:enrollment_id>', methods=['POST'])
@login_required
@role_required('teacher')
def teacher_edit_grade(enrollment_id):
    """Edit a student's grade"""
    teacher_id = session.get('user_id')
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Verify teacher teaches this course
    teacher_course = TeacherCourse.query.filter_by(teacher_id=teacher_id, course_id=enrollment.course_id).first()
    if not teacher_course:
        flash('You do not have permission to edit grades for this course.', 'danger')
        return redirect(url_for('teacher_courses'))
    
    try:
        grade_value = float(request.form.get('grade', 0))
        if grade_value < 0 or grade_value > 100:
            flash('Grade must be between 0 and 100.', 'danger')
            return redirect(url_for('teacher_course_detail', course_id=enrollment.course_id))
    except (ValueError, TypeError):
        flash('Invalid grade value.', 'danger')
        return redirect(url_for('teacher_course_detail', course_id=enrollment.course_id))
    
    # Update or create grade
    if enrollment.grade:
        enrollment.grade.grade_value = grade_value
    else:
        new_grade = Grade(enrollment_id=enrollment_id, grade_value=grade_value)
        db.session.add(new_grade)
    
    db.session.commit()
    flash('Grade updated successfully.', 'success')
    return redirect(url_for('teacher_course_detail', course_id=enrollment.course_id))

# ===== ADMIN ROUTES =====
# Admin functionality is handled by Flask-Admin at /admin

# ===== API ROUTES (for AJAX if needed) =====

@app.route('/api/course/<int:course_id>/enrollment_count')
@login_required
def api_enrollment_count(course_id):
    """API endpoint to get enrollment count for a course"""
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'course_id': course_id,
        'enrolled': course.get_enrollment_count(),
        'capacity': course.capacity,
        'available': course.capacity - course.get_enrollment_count(),
        'is_full': course.is_full()
    })

# ===== INITIALIZATION =====

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if User.query.count() > 0:
            return
        
        # Create sample admin
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        
        # Create sample students
        student1 = User(
            username='student1',
            password_hash=generate_password_hash('student123'),
            role='student'
        )
        student2 = User(
            username='student2',
            password_hash=generate_password_hash('student123'),
            role='student'
        )
        db.session.add_all([student1, student2])
        
        # Create sample teacher
        teacher1 = User(
            username='teacher1',
            password_hash=generate_password_hash('teacher123'),
            role='teacher'
        )
        db.session.add(teacher1)
        
        db.session.commit()
        
        # Create sample courses
        course1 = Course(name='Introduction to Computer Science', department='CS', capacity=30)
        course2 = Course(name='Data Structures', department='CS', capacity=25)
        course3 = Course(name='Web Development', department='CS', capacity=20)
        db.session.add_all([course1, course2, course3])
        db.session.commit()
        
        # Assign teacher to courses
        tc1 = TeacherCourse(teacher_id=teacher1.id, course_id=course1.id)
        tc2 = TeacherCourse(teacher_id=teacher1.id, course_id=course2.id)
        db.session.add_all([tc1, tc2])
        db.session.commit()
        
        # Create sample enrollments
        enrollment1 = Enrollment(user_id=student1.id, course_id=course1.id)
        enrollment2 = Enrollment(user_id=student1.id, course_id=course2.id)
        enrollment3 = Enrollment(user_id=student2.id, course_id=course1.id)
        db.session.add_all([enrollment1, enrollment2, enrollment3])
        db.session.commit()
        
        # Create sample grades
        grade1 = Grade(enrollment_id=enrollment1.id, grade_value=85.5)
        grade2 = Grade(enrollment_id=enrollment2.id, grade_value=92.0)
        grade3 = Grade(enrollment_id=enrollment3.id, grade_value=78.5)
        db.session.add_all([grade1, grade2, grade3])
        db.session.commit()
        
        print("Database initialized with sample data")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

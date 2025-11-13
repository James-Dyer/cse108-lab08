from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, admin
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # Relationships
    taught_classes = db.relationship('Class', backref='teacher', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., CSE 162
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='class_obj', lazy=True, cascade='all, delete-orphan')
    
    @property
    def current_enrollment(self):
        """Dynamic count of enrolled students"""
        return len(self.enrollments)
    
    def __repr__(self):
        return f'<Class {self.course_code}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True)  # Nullable, teacher can set later
    
    # Unique constraint: a student can only enroll once per class
    __table_args__ = (db.UniqueConstraint('student_id', 'class_id', name='unique_student_class'),)
    
    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} Class:{self.class_id}>'


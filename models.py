from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Brute-force protection fields
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), unique=True, nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # e.g., "6 Months"
    fee = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active / Inactive

    def __repr__(self):
        return f"<Course {self.course_name}>"

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., FTCI2026001
    photo = db.Column(db.String(255), nullable=True)  # filename in uploads
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    alternate_mobile = db.Column(db.String(10), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    education = db.Column(db.String(100), nullable=False)
    
    # Course Details
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # Auto-filled from course, but editable
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    admission_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    completion_date = db.Column(db.Date, nullable=True)
    certificate_number = db.Column(db.String(50), unique=True, nullable=True)
    
    # Fee Details
    total_fee = db.Column(db.Float, nullable=False)
    registration_fee = db.Column(db.Float, default=0.0, nullable=False)
    discount = db.Column(db.Float, default=0.0, nullable=False)
    paid_fee = db.Column(db.Float, default=0.0, nullable=False)
    pending_fee = db.Column(db.Float, nullable=False)  # Auto-calculated
    
    # Receipt info on creation
    payment_method = db.Column(db.String(20), nullable=False)  # Cash / UPI / Bank Transfer / Card
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active / Completed
    
    # Study Center Code
    study_center_code = db.Column(db.String(50), default='P22', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref=db.backref('students', lazy='dynamic'))

    def __repr__(self):
        return f"<Student {self.full_name} ({self.student_id})>"

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # Cash / UPI / Bank Transfer / Card
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('all_payments', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Payment {self.receipt_number} - {self.amount}>"

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    institute_name = db.Column(db.String(255), default='FutureTech Computer Institute', nullable=False)
    logo = db.Column(db.String(255), nullable=True)  # filename in static/branding
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    study_center_code = db.Column(db.String(50), default='P22', nullable=False)
    receipt_footer = db.Column(db.Text, nullable=True)
    certificate_signature = db.Column(db.String(255), nullable=True)  # filename of signature or text

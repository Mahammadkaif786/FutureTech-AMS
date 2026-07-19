from flask import Blueprint, render_template, jsonify, g
from flask_login import login_required
from datetime import date, datetime, timedelta
from models import Student, Course, Payment, db
import calendar
from collections import OrderedDict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    
    # 1. Metric Calculations
    total_students = Student.query.count()
    active_students = Student.query.filter_by(status='Active').count()
    completed_students = Student.query.filter_by(status='Completed').count()
    total_courses = Course.query.filter_by(status='Active').count()
    
    # Financial collection aggregates
    total_collected = db.session.query(db.func.sum(Payment.amount)).scalar() or 0.0
    total_pending = db.session.query(db.func.sum(Student.pending_fee)).scalar() or 0.0
    
    # Admissions for the current date
    today_admissions = Student.query.filter_by(admission_date=today).count()
    
    # Last 10 Student Admissions
    recent_admissions = Student.query.order_by(Student.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html',
                           total_students=total_students,
                           active_students=active_students,
                           completed_students=completed_students,
                           total_courses=total_courses,
                           total_collected=total_collected,
                           total_pending=total_pending,
                           today_admissions=today_admissions,
                           recent_admissions=recent_admissions,
                           active_page='dashboard')

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def charts_data():
    """
    Returns monthly admissions numbers (last 6 months) and 
    fee collections ratios in JSON format for client Chart.js components.
    """
    today = date.today()
    months_list = []
    
    # Generate list of past 6 months (year, month, label)
    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        label = f"{calendar.month_abbr[month]} {year}"
        months_list.append((year, month, label))
        
    # Build ordering dict
    admissions_chart = OrderedDict((item[2], 0) for item in months_list)
    
    # Query student records from start range
    start_date = date(months_list[0][0], months_list[0][1], 1)
    students = Student.query.filter(Student.admission_date >= start_date).all()
    
    for s in students:
        s_date = s.admission_date
        s_label = f"{calendar.month_abbr[s_date.month]} {s_date.year}"
        if s_label in admissions_chart:
            admissions_chart[s_label] += 1
            
    # Query fee summary totals
    total_paid = db.session.query(db.func.sum(Payment.amount)).scalar() or 0.0
    total_pending = db.session.query(db.func.sum(Student.pending_fee)).scalar() or 0.0
    
    return jsonify({
        'admissions': {
            'labels': list(admissions_chart.keys()),
            'data': list(admissions_chart.values())
        },
        'fees': {
            'labels': ['Collected Fees (INR)', 'Pending Fees (INR)'],
            'data': [total_paid, total_pending]
        }
    })

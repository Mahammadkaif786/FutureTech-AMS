from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_required
from models import Student, Course, Payment, db
from datetime import date

print_bp = Blueprint('print', __name__)

@print_bp.route('/print/admission/<int:id>')
@login_required
def print_admission(id):
    student = Student.query.get_or_404(id)
    return render_template('print/admission.html', student=student)

@print_bp.route('/print/receipt/<string:receipt_number>')
@login_required
def print_receipt(receipt_number):
    # Try finding in payments table first (individual collect payments)
    payment = Payment.query.filter_by(receipt_number=receipt_number).first()
    
    if payment:
        student = Student.query.get(payment.student_id)
        # If this payment matches the student's initial receipt_number
        is_initial = (student.receipt_number == receipt_number)
        return render_template('print/receipt.html', student=student, payment=payment, is_initial=is_initial)
        
    # If not in payments, check if it's the student's initial receipt record with 0 initial payment
    student = Student.query.filter_by(receipt_number=receipt_number).first()
    if student:
        dummy_payment = Payment(
            student_id=student.id,
            amount=student.paid_fee,
            payment_method=student.payment_method,
            receipt_number=student.receipt_number,
            payment_date=student.admission_date
        )
        return render_template('print/receipt.html', student=student, payment=dummy_payment, is_initial=True)
        
    flash("Receipt record not found.", "danger")
    return redirect(url_for('dashboard.index'))

@print_bp.route('/print/id_card/<int:id>')
@login_required
def print_id_card(id):
    student = Student.query.get_or_404(id)
    return render_template('print/id_card.html', student=student)

@print_bp.route('/print/profile/<int:id>')
@login_required
def print_profile(id):
    student = Student.query.get_or_404(id)
    payments = Payment.query.filter_by(student_id=student.id).order_by(Payment.payment_date.asc()).all()
    return render_template('print/profile.html', student=student, payments=payments)

@print_bp.route('/print/certificate/<int:id>')
@login_required
def print_certificate(id):
    student = Student.query.get_or_404(id)
    if student.status != 'Completed':
        # Block printing certificate if status is active
        flash("Certificate cannot be printed. The student has not completed their course.", "danger")
        return redirect(url_for('students.view_student', id=student.id))
        
    return render_template('print/certificate.html', student=student)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from datetime import datetime
from models import Student, Payment, db
from utils import generate_receipt_number

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/fees')
@login_required
def index():
    search_q = request.args.get('search', '')
    
    query = Student.query
    if search_q:
        query = query.filter(
            (Student.full_name.like(f"%{search_q}%")) |
            (Student.student_id.like(f"%{search_q}%")) |
            (Student.receipt_number.like(f"%{search_q}%"))
        )
        
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Student.student_id.desc()).paginate(page=page, per_page=15, error_out=False)
    students = pagination.items
    
    return render_template('fees/list.html',
                           students=students,
                           pagination=pagination,
                           search_q=search_q,
                           active_page='fees')

@fees_bp.route('/fees/collect/<int:student_id>', methods=['POST'])
@login_required
def collect_payment(student_id):
    student = Student.query.get_or_404(student_id)
    
    amount = request.form.get('amount', type=float)
    payment_method = request.form.get('payment_method', 'Cash')
    
    # Validation constraints
    if not amount or amount <= 0:
        flash("Fee collection error: Invalid payment amount. Must be greater than 0.", "danger")
        return redirect(request.referrer or url_for('students.view_student', id=student.id))
        
    if amount > student.pending_fee:
        # Prevent payment collection exceeding dues balance
        flash(f"Fee collection error: Amount exceeds pending balance of ₹{student.pending_fee:.2f}.", "danger")
        return redirect(request.referrer or url_for('students.view_student', id=student.id))
        
    # Process transactional Payment
    receipt = generate_receipt_number()
    payment = Payment(
        student_id=student.id,
        amount=amount,
        payment_method=payment_method,
        receipt_number=receipt,
        payment_date=datetime.utcnow()
    )
    db.session.add(payment)
    
    # Recalculate Student fee summary values
    student.paid_fee += amount
    student.pending_fee = student.total_fee - student.discount - student.paid_fee
    
    db.session.commit()
    flash(f"Payment of ₹{amount:,.2f} recorded. Receipt: {receipt}", "success")
    return redirect(request.referrer or url_for('students.view_student', id=student.id))

@fees_bp.route('/fees/history/<int:student_id>')
@login_required
def history(student_id):
    student = Student.query.get_or_404(student_id)
    payments = Payment.query.filter_by(student_id=student.id).order_by(Payment.payment_date.desc()).all()
    return render_template('fees/history.html', student=student, payments=payments, active_page='fees')

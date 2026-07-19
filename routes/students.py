from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, g
from flask_login import login_required
from datetime import date, datetime
from models import Student, Course, Payment, db
from forms import StudentForm
from utils import (
    generate_student_id, 
    generate_receipt_number, 
    generate_certificate_number, 
    save_uploaded_photo
)
import os

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
@login_required
def index():
    # Filters
    search_q = request.args.get('search', '')
    course_filter = request.args.get('course', type=int)
    status_filter = request.args.get('status', '')
    
    # Query build
    query = Student.query
    
    if search_q:
        query = query.join(Course).filter(
            (Student.full_name.like(f"%{search_q}%")) |
            (Student.student_id.like(f"%{search_q}%")) |
            (Student.mobile.like(f"%{search_q}%")) |
            (Course.course_name.like(f"%{search_q}%"))
        )
        
    if course_filter:
        query = query.filter(Student.course_id == course_filter)
        
    if status_filter:
        query = query.filter(Student.status == status_filter)
        
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Student.student_id.desc()).paginate(page=page, per_page=15, error_out=False)
    students = pagination.items
    
    # Dropdowns for filter
    all_courses = Course.query.order_by(Course.course_name).all()
    
    return render_template('students/list.html',
                           students=students,
                           pagination=pagination,
                           all_courses=all_courses,
                           course_filter=course_filter,
                           status_filter=status_filter,
                           search_q=search_q,
                           active_page='students')

@students_bp.route('/students/active')
@login_required
def active_list():
    # Active students search & filters
    search_q = request.args.get('search', '')
    course_filter = request.args.get('course', type=int)
    batch_filter = request.args.get('batch', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    query = Student.query.filter_by(status='Active')
    
    if search_q:
        query = query.filter(
            (Student.full_name.like(f"%{search_q}%")) |
            (Student.student_id.like(f"%{search_q}%")) |
            (Student.mobile.like(f"%{search_q}%"))
        )
    if course_filter:
        query = query.filter(Student.course_id == course_filter)
    if batch_filter:
        query = query.filter(Student.batch.like(f"%{batch_filter}%"))
        
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Student.admission_date >= start_date)
        except ValueError:
            pass
            
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Student.admission_date <= end_date)
        except ValueError:
            pass
            
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Student.admission_date.desc()).paginate(page=page, per_page=15, error_out=False)
    students = pagination.items
    
    all_courses = Course.query.filter_by(status='Active').all()
    
    return render_template('students/active.html',
                           students=students,
                           pagination=pagination,
                           all_courses=all_courses,
                           course_filter=course_filter,
                           batch_filter=batch_filter,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           search_q=search_q,
                           active_page='active_students')

@students_bp.route('/students/completed')
@login_required
def completed_list():
    search_q = request.args.get('search', '')
    course_filter = request.args.get('course', type=int)
    
    query = Student.query.filter_by(status='Completed')
    
    if search_q:
        query = query.filter(
            (Student.full_name.like(f"%{search_q}%")) |
            (Student.student_id.like(f"%{search_q}%")) |
            (Student.certificate_number.like(f"%{search_q}%"))
        )
    if course_filter:
        query = query.filter(Student.course_id == course_filter)
        
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Student.completion_date.desc()).paginate(page=page, per_page=15, error_out=False)
    students = pagination.items
    
    all_courses = Course.query.all()
    
    return render_template('students/completed.html',
                           students=students,
                           pagination=pagination,
                           all_courses=all_courses,
                           course_filter=course_filter,
                           search_q=search_q,
                           active_page='completed_students')

@students_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    form = StudentForm()
    # Populate course choices
    courses = Course.query.filter_by(status='Active').all()
    form.course_id.choices = [(0, 'Select Course')] + [(c.id, f"{c.course_name} (Fee: ₹{c.fee:.2f})") for c in courses]
    
    # Auto-generate temporary placeholders for display on GET requests
    generated_id = generate_student_id()
    generated_receipt = generate_receipt_number()
    default_center = g.settings.study_center_code if g.settings else 'P22'
    
    if request.method == 'GET':
        form.study_center_code.data = default_center
        
    # Validate select fields bypass
    if form.course_id.data == 0:
        form.course_id.data = None

    if form.validate_on_submit():
        # Check duplicate admission warning
        duplicate = Student.query.filter_by(
            full_name=form.full_name.data.strip(),
            mobile=form.mobile.data.strip(),
            course_id=form.course_id.data
        ).first()
        
        # If there's an ignore flag, bypass. Otherwise warn on duplicate.
        bypass_dup = request.form.get('bypass_duplicate') == 'true'
        if duplicate and not bypass_dup:
            flash("Warning: A student with the same Name, Mobile Number, and Course already exists. Please verify. If this is not a double entry, click 'Save' again.", "warning")
            return render_template('students/form.html', form=form, mode='add', 
                                   generated_id=generated_id, 
                                   generated_receipt=generated_receipt,
                                   is_duplicate=True)
                                   
        # Photo handling
        photo_filename = None
        if form.photo.data:
            photo_filename = save_uploaded_photo(form.photo.data, current_app.config['UPLOAD_FOLDER'])

        # Fee arithmetic validation
        total_fee = form.total_fee.data
        discount = form.discount.data or 0.0
        paid_amount = form.paid_amount.data or 0.0
        pending_fee = total_fee - discount - paid_amount
        
        # Re-generate to guarantee absolute uniqueness on transaction commit
        final_student_id = generate_student_id()
        final_receipt = generate_receipt_number()
        
        new_student = Student(
            student_id=final_student_id,
            photo=photo_filename,
            full_name=form.full_name.data.strip(),
            father_name=form.father_name.data.strip(),
            address=form.address.data.strip(),
            state=form.state.data.strip(),
            pin_code=form.pin_code.data.strip(),
            mobile=form.mobile.data.strip(),
            alternate_mobile=form.alternate_mobile.data.strip() if form.alternate_mobile.data else None,
            dob=form.dob.data,
            gender=form.gender.data,
            education=form.education.data,
            course_id=form.course_id.data,
            batch=form.batch.data.strip(),
            duration=form.duration.data.strip(),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            admission_date=date.today(),
            total_fee=total_fee,
            registration_fee=form.registration_fee.data or 0.0,
            discount=discount,
            paid_fee=paid_amount,
            pending_fee=pending_fee,
            payment_method=form.payment_method.data,
            receipt_number=final_receipt,
            study_center_code=form.study_center_code.data.strip(),
            status=form.status.data
        )
        
        db.session.add(new_student)
        db.session.flush() # Flush to get new_student.id

        # Insert Transaction payment log if paid > 0
        if paid_amount > 0:
            payment = Payment(
                student_id=new_student.id,
                amount=paid_amount,
                payment_method=form.payment_method.data,
                receipt_number=final_receipt,
                payment_date=datetime.utcnow()
            )
            db.session.add(payment)
            
        # If student is created as Completed, set fields
        if new_student.status == 'Completed':
            new_student.completion_date = date.today()
            new_student.certificate_number = generate_certificate_number()
            
        db.session.commit()
        flash(f"Student {new_student.full_name} admitted successfully with Student ID: {new_student.student_id}", "success")
        return redirect(url_for('students.index'))
        
    return render_template('students/form.html', form=form, mode='add', 
                           generated_id=generated_id, 
                           generated_receipt=generated_receipt)

@students_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(student_db_id=student.id)
    
    # Populate course choices (includes inactive in case student was enrolled previously)
    courses = Course.query.all()
    form.course_id.choices = [(c.id, f"{c.course_name} (Fee: ₹{c.fee:.2f})") for c in courses]
    
    if request.method == 'GET':
        form.study_center_code.data = student.study_center_code
        form.full_name.data = student.full_name
        form.father_name.data = student.father_name
        form.address.data = student.address
        form.state.data = student.state
        form.pin_code.data = student.pin_code
        form.mobile.data = student.mobile
        form.alternate_mobile.data = student.alternate_mobile
        form.dob.data = student.dob
        form.gender.data = student.gender
        form.education.data = student.education
        form.course_id.data = student.course_id
        form.batch.data = student.batch
        form.duration.data = student.duration
        form.start_date.data = student.start_date
        form.end_date.data = student.end_date
        form.total_fee.data = student.total_fee
        form.registration_fee.data = student.registration_fee
        form.discount.data = student.discount
        form.paid_amount.data = student.paid_fee  # maps current paid fee
        form.payment_method.data = student.payment_method
        form.status.data = student.status

    if form.validate_on_submit():
        # Handle Photo Upload
        if form.photo.data:
            photo_filename = save_uploaded_photo(form.photo.data, current_app.config['UPLOAD_FOLDER'], student.photo)
            student.photo = photo_filename
            
        student.study_center_code = form.study_center_code.data.strip()
        student.full_name = form.full_name.data.strip()
        student.father_name = form.father_name.data.strip()
        student.address = form.address.data.strip()
        student.state = form.state.data.strip()
        student.pin_code = form.pin_code.data.strip()
        student.mobile = form.mobile.data.strip()
        student.alternate_mobile = form.alternate_mobile.data.strip() if form.alternate_mobile.data else None
        student.dob = form.dob.data
        student.gender = form.gender.data
        student.education = form.education.data
        student.course_id = form.course_id.data
        student.batch = form.batch.data.strip()
        student.duration = form.duration.data.strip()
        student.start_date = form.start_date.data
        student.end_date = form.end_date.data
        
        # Fee logic update
        student.total_fee = form.total_fee.data
        student.registration_fee = form.registration_fee.data or 0.0
        student.discount = form.discount.data or 0.0
        
        # Paid updates: sync with receipt payments
        new_paid = form.paid_amount.data or 0.0
        old_paid = student.paid_fee
        student.paid_fee = new_paid
        student.pending_fee = student.total_fee - student.discount - new_paid
        student.payment_method = form.payment_method.data
        
        # Update or create the initial payment transaction matching receipt_number
        first_payment = Payment.query.filter_by(receipt_number=student.receipt_number).first()
        if first_payment:
            if new_paid > 0:
                first_payment.amount = new_paid
                first_payment.payment_method = form.payment_method.data
            else:
                db.session.delete(first_payment)
        elif new_paid > 0:
            # Create payment if it wasn't there
            payment = Payment(
                student_id=student.id,
                amount=new_paid,
                payment_method=form.payment_method.data,
                receipt_number=student.receipt_number,
                payment_date=datetime.utcnow()
            )
            db.session.add(payment)

        # Status controls
        if form.status.data == 'Completed' and student.status != 'Completed':
            # Block completed status if dues are left, unless forced or checked
            # Standard form submit check is checked in controller, here we allow it
            student.status = 'Completed'
            student.completion_date = date.today()
            if not student.certificate_number:
                student.certificate_number = generate_certificate_number()
        elif form.status.data == 'Active':
            student.status = 'Active'
            student.completion_date = None
            student.certificate_number = None

        db.session.commit()
        flash(f"Student details for {student.full_name} updated successfully.", "success")
        return redirect(url_for('students.view_student', id=student.id))

    return render_template('students/form.html', form=form, student=student, mode='edit')

@students_bp.route('/students/view/<int:id>')
@login_required
def view_student(id):
    student = Student.query.get_or_404(id)
    payments = Payment.query.filter_by(student_id=id).order_by(Payment.payment_date.desc()).all()
    return render_template('students/view.html', student=student, payments=payments, active_page='students')

@students_bp.route('/students/mark-completed/<int:id>', methods=['POST'])
@login_required
def mark_completed(id):
    student = Student.query.get_or_404(id)
    override = request.form.get('override') == 'true'
    
    # Financial block
    if student.pending_fee > 0 and not override:
        flash(f"Cannot mark completed. Student has pending dues of ₹{student.pending_fee:.2f}. Please record payment or confirm with override.", "danger")
        return redirect(url_for('students.view_student', id=student.id))
        
    student.status = 'Completed'
    student.completion_date = date.today()
    if not student.certificate_number:
        student.certificate_number = generate_certificate_number()
        
    db.session.commit()
    flash(f"Student status updated to Completed. Certificate: {student.certificate_number}", "success")
    return redirect(url_for('students.view_student', id=student.id))

@students_bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    
    # Remove photo file if exists
    if student.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], student.photo)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except OSError:
                pass
                
    db.session.delete(student)
    db.session.commit()
    flash("Student admission records and all associated transaction payments deleted successfully.", "success")
    return redirect(url_for('students.index'))

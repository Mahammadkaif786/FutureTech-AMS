from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import Course, Student, db
from forms import CourseForm

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['GET', 'POST'])
@login_required
def index():
    form = CourseForm()
    
    # Check if editing an existing course
    edit_id = request.args.get('edit_id', type=int)
    edit_course = None
    if edit_id:
        edit_course = Course.query.get_or_404(edit_id)
        if request.method == 'GET':
            form.course_name.data = edit_course.course_name
            form.duration.data = edit_course.duration
            form.fee.data = edit_course.fee
            form.description.data = edit_course.description
            form.status.data = edit_course.status
            
    if form.validate_on_submit():
        # Duplicate course name validator
        existing = Course.query.filter_by(course_name=form.course_name.data).first()
        if existing and (not edit_id or existing.id != edit_id):
            flash("A course with this name already exists. Please choose a unique name.", "danger")
        else:
            if edit_course:
                # Update properties
                edit_course.course_name = form.course_name.data
                edit_course.duration = form.duration.data
                edit_course.fee = form.fee.data
                edit_course.description = form.description.data
                edit_course.status = form.status.data
                db.session.commit()
                flash(f"Course '{edit_course.course_name}' updated successfully!", "success")
                return redirect(url_for('courses.index'))
            else:
                # Insert new course
                new_course = Course(
                    course_name=form.course_name.data,
                    duration=form.duration.data,
                    fee=form.fee.data,
                    description=form.description.data,
                    status=form.status.data
                )
                db.session.add(new_course)
                db.session.commit()
                flash(f"New course '{new_course.course_name}' added successfully!", "success")
                return redirect(url_for('courses.index'))
                
    # Search course logic
    search_q = request.args.get('search', '')
    query = Course.query
    if search_q:
        query = query.filter(Course.course_name.like(f"%{search_q}%"))
        
    courses = query.order_by(Course.course_name).all()
    
    return render_template('courses/list.html',
                           courses=courses,
                           form=form,
                           edit_course=edit_course,
                           search_q=search_q,
                           active_page='courses')

@courses_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    
    # Validation constraint: check if students are active or enrolled in this course
    enrolled_count = Student.query.filter_by(course_id=id).count()
    if enrolled_count > 0:
        flash(f"Cannot delete '{course.course_name}'. There are {enrolled_count} student(s) currently enrolled. You can set the course status to 'Inactive' instead to halt new admissions.", "danger")
    else:
        db.session.delete(course)
        db.session.commit()
        flash("Course deleted successfully!", "success")
        
    return redirect(url_for('courses.index'))

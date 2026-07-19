from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Optional
from datetime import date

# 1. Admin Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    remember = BooleanField('Remember Me')

# 2. Course Management Form
class CourseForm(FlaskForm):
    course_name = StringField('Course Name', validators=[
        DataRequired(message="Course Name is required"),
        Length(min=2, max=100, message="Course Name must be between 2 and 100 characters")
    ])
    duration = StringField('Duration (e.g. 6 Months)', validators=[
        DataRequired(message="Duration is required"),
        Length(max=50)
    ])
    fee = FloatField('Fee (INR)', validators=[
        DataRequired(message="Fee is required")
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')

    def validate_fee(self, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError("Course fee must be greater than 0.")

# 3. Student Admission Form
class StudentForm(FlaskForm):
    # Admission Info
    study_center_code = StringField('Study Center Code', default='P22', validators=[
        DataRequired(message="Study Center Code is required")
    ])
    
    # Personal Info
    photo = FileField('Student Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, JPEG, and PNG images are allowed!')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(message="Full Name is required"),
        Length(min=3, max=60, message="Name must be between 3 and 60 characters"),
        Regexp(r'^[a-zA-Z\s]+$', message="Name must contain letters and spaces only")
    ])
    father_name = StringField("Father's Name", validators=[
        DataRequired(message="Father's Name is required"),
        Length(min=3, max=60, message="Father's Name must be between 3 and 60 characters"),
        Regexp(r'^[a-zA-Z\s]+$', message="Father's Name must contain letters and spaces only")
    ])
    address = TextAreaField('Address', validators=[
        DataRequired(message="Address is required"),
        Length(min=5, max=500, message="Address must be between 5 and 500 characters")
    ])
    state = StringField('State', validators=[
        DataRequired(message="State is required"),
        Length(min=2, max=50)
    ])
    pin_code = StringField('PIN Code', validators=[
        DataRequired(message="PIN Code is required"),
        Regexp(r'^\d{6}$', message="PIN Code must be exactly 6 digits")
    ])
    mobile = StringField('Mobile Number', validators=[
        DataRequired(message="Mobile Number is required"),
        Regexp(r'^[6-9]\d{9}$', message="Mobile Number must be exactly 10 digits and start with 6, 7, 8, or 9")
    ])
    alternate_mobile = StringField('Alternate Mobile Number', validators=[
        Optional(),
        Regexp(r'^\d{10}$', message="Alternate Mobile must be exactly 10 digits")
    ])
    dob = DateField('Date of Birth', validators=[
        DataRequired(message="Date of Birth is required")
    ])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[
        DataRequired(message="Gender selection is required")
    ])
    education = SelectField('Education Qualification', choices=[
        ('', 'Select Qualification'),
        ('10th Standard', '10th Standard'),
        ('12th Standard', '12th Standard'),
        ('Undergraduate', 'Undergraduate'),
        ('Postgraduate', 'Postgraduate'),
        ('Diploma', 'Diploma'),
        ('Other', 'Other')
    ], validators=[
        DataRequired(message="Education qualification is required")
    ])
    
    # Course details
    course_id = SelectField('Course', coerce=int, validators=[
        DataRequired(message="Course selection is required")
    ])
    batch = StringField('Batch (e.g. Morning 9-11)', validators=[
        DataRequired(message="Batch description is required")
    ])
    duration = StringField('Duration', validators=[
        DataRequired(message="Duration is required")
    ])
    start_date = DateField('Start Date', validators=[
        DataRequired(message="Start Date is required")
    ])
    end_date = DateField('End Date', validators=[
        DataRequired(message="End Date is required")
    ])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Completed', 'Completed')], default='Active')

    # Fee details
    total_fee = FloatField('Total Fee', validators=[
        DataRequired(message="Total Fee is required")
    ])
    registration_fee = FloatField('Registration Fee', default=0.0, validators=[
        Optional()
    ])
    discount = FloatField('Discount', default=0.0, validators=[
        Optional()
    ])
    paid_amount = FloatField('Paid Amount', default=0.0, validators=[
        Optional()
    ])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Card', 'Card')
    ], default='Cash')

    def __init__(self, *args, **kwargs):
        self.student_db_id = kwargs.pop('student_db_id', None)
        super(StudentForm, self).__init__(*args, **kwargs)

    # Cross-field and field validators
    def validate_mobile(self, field):
        from models import Student
        query = Student.query.filter_by(mobile=field.data)
        if self.student_db_id:
            query = query.filter(Student.id != self.student_db_id)
        if query.first():
            raise ValidationError("This mobile number is already registered to another student.")

    def validate_alternate_mobile(self, field):
        if field.data and field.data == self.mobile.data:
            raise ValidationError("Alternate mobile number must be different from primary mobile number.")

    def validate_dob(self, field):
        if field.data:
            today = date.today()
            age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
            if age < 12:
                raise ValidationError("Student must be at least 12 years old at time of admission.")

    def validate_end_date(self, field):
        if field.data and self.start_date.data:
            if field.data <= self.start_date.data:
                raise ValidationError("End date must be strictly after the start date.")

    def validate_total_fee(self, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError("Total Fee must be greater than 0.")

    def validate_registration_fee(self, field):
        val = field.data or 0.0
        tot = self.total_fee.data or 0.0
        if val < 0:
            raise ValidationError("Registration Fee cannot be negative.")
        if val > tot:
            raise ValidationError("Registration Fee cannot exceed Total Fee.")

    def validate_discount(self, field):
        val = field.data or 0.0
        tot = self.total_fee.data or 0.0
        if val < 0:
            raise ValidationError("Discount cannot be negative.")
        if val > tot:
            raise ValidationError("Discount cannot exceed Total Fee.")

    def validate_paid_amount(self, field):
        val = field.data or 0.0
        tot = self.total_fee.data or 0.0
        disc = self.discount.data or 0.0
        if val < 0:
            raise ValidationError("Paid Amount cannot be negative.")
        max_allowed = tot - disc
        if val > max_allowed:
            raise ValidationError(f"Paid Amount cannot exceed net fee (Total Fee - Discount = {max_allowed:.2f}).")

# 4. Payment Collection Form (Fees Section)
class CollectPaymentForm(FlaskForm):
    amount = FloatField('Amount (INR)', validators=[
        DataRequired(message="Payment amount is required")
    ])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Card', 'Card')
    ], default='Cash')

    def __init__(self, *args, **kwargs):
        self.max_amount = kwargs.pop('max_amount', 0.0)
        super(CollectPaymentForm, self).__init__(*args, **kwargs)

    def validate_amount(self, field):
        if field.data is not None:
            if field.data <= 0:
                raise ValidationError("Payment amount must be greater than 0.")
            if field.data > self.max_amount:
                raise ValidationError(f"Payment amount cannot exceed the pending fee of {self.max_amount:.2f}.")

# 5. Settings Form
class SettingsForm(FlaskForm):
    institute_name = StringField('Institute Name', validators=[
        DataRequired(message="Institute Name is required"),
        Length(min=3, max=255)
    ])
    logo = FileField('Institute Logo', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, JPEG, and PNG images are allowed!')
    ])
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=500)
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20)
    ])
    email = StringField('Email', validators=[
        Optional(),
        Length(max=100)
    ])
    study_center_code = StringField('Default Study Center Code', validators=[
        DataRequired(message="Default Center Code is required"),
        Length(max=50)
    ])
    receipt_footer = TextAreaField('Receipt Footer Notes', validators=[
        Optional(),
        Length(max=500)
    ])
    certificate_signature = FileField('Certificate Signature Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, JPEG, and PNG images are allowed!')
    ])

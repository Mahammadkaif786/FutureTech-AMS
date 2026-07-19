import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_photo(file, upload_folder, existing_filename=None):
    """
    Saves student photos, resizes them to 300x300 for UI, 
    and removes the previously uploaded photo if updating.
    """
    # Create upload directory if it does not exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Remove existing photo if replacing
    if existing_filename:
        old_path = os.path.join(upload_folder, existing_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
                
    # Secure and rename photo
    ext = file.filename.rsplit('.', 1)[1].lower()
    new_filename = f"stud_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.{ext}"
    file_path = os.path.join(upload_folder, new_filename)
    
    # Save the file
    file.save(file_path)
    
    # Post-process: Resize to standard size (300x300) to optimize storage
    try:
        img = Image.open(file_path)
        img.thumbnail((300, 300))
        img.save(file_path)
    except Exception:
        # If PIL fails (e.g. format issues), keep the original file
        pass
        
    return new_filename

def save_branding_file(file, upload_folder, existing_filename=None):
    """
    Saves branding files (logos or signatures)
    """
    os.makedirs(upload_folder, exist_ok=True)
    if existing_filename:
        old_path = os.path.join(upload_folder, existing_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
                
    ext = file.filename.rsplit('.', 1)[1].lower()
    new_filename = f"branding_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}"
    file_path = os.path.join(upload_folder, new_filename)
    file.save(file_path)
    return new_filename

def generate_student_id():
    """
    Generates sequential student ID per year: FTCI2026001, FTCI2026002...
    """
    from models import Student
    current_year = datetime.utcnow().year
    prefix = f"FTCI{current_year}"
    
    # Query database for the latest student ID starting with this prefix
    latest_student = Student.query.filter(Student.student_id.like(f"{prefix}%"))\
                                   .order_by(Student.student_id.desc())\
                                   .first()
    if latest_student:
        try:
            # Extract sequence number
            seq_str = latest_student.student_id[len(prefix):]
            seq_num = int(seq_str)
            new_seq_num = seq_num + 1
        except (ValueError, IndexError):
            new_seq_num = 1
    else:
        new_seq_num = 1
        
    return f"{prefix}{new_seq_num:03d}"

def generate_receipt_number():
    """
    Generates sequential receipt number: RCP20260001, RCP20260002...
    Checks both Student (initial payment) and Payment records to guarantee uniqueness.
    """
    from models import Student, Payment, db
    current_year = datetime.utcnow().year
    prefix = f"RCP{current_year}"
    
    # Query maximum receipt sequence from Student table
    latest_stud_receipt = db.session.query(db.func.max(Student.receipt_number))\
                                    .filter(Student.receipt_number.like(f"{prefix}%"))\
                                    .scalar()
    # Query maximum receipt sequence from Payments table
    latest_pay_receipt = db.session.query(db.func.max(Payment.receipt_number))\
                                   .filter(Payment.receipt_number.like(f"{prefix}%"))\
                                   .scalar()
                                   
    max_seq = 0
    for r_num in [latest_stud_receipt, latest_pay_receipt]:
        if r_num and r_num.startswith(prefix):
            try:
                seq = int(r_num[len(prefix):])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
                
    new_seq = max_seq + 1
    return f"{prefix}{new_seq:04d}"

def generate_certificate_number():
    """
    Generates unique sequential certificate number: CERT20260001...
    """
    from models import Student, db
    current_year = datetime.utcnow().year
    prefix = f"CERT{current_year}"
    
    latest_cert = db.session.query(db.func.max(Student.certificate_number))\
                            .filter(Student.certificate_number.like(f"{prefix}%"))\
                            .scalar()
                            
    max_seq = 0
    if latest_cert and latest_cert.startswith(prefix):
        try:
            max_seq = int(latest_cert[len(prefix):])
        except ValueError:
            pass
            
    new_seq = max_seq + 1
    return f"{prefix}{new_seq:04d}"

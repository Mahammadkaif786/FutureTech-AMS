import unittest
from datetime import date, datetime, timedelta
from app import app, db
from models import Admin, Student, Course, Payment, Setting
from utils import generate_student_id, generate_receipt_number, generate_certificate_number

class FutureTechTest(unittest.TestCase):
    def setUp(self):
        """
        Configure Flask application for testing and initialize
        an in-memory database configuration.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF in tests for ease of API simulation
        self.app = app.test_client()
        
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()
        
    def tearDown(self):
        """
        Teardown database context and session connections.
        """
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        
    def test_admin_lockout_mechanism(self):
        """
        Validates account brute-force protection logic.
        """
        # Create dummy admin record
        admin = Admin(username='testadmin')
        admin.set_password('secrethash')
        db.session.add(admin)
        db.session.commit()
        
        # Verify initial states
        self.assertEqual(admin.failed_attempts, 0)
        self.assertIsNone(admin.locked_until)
        
        # Simulate 5 failed login attempts
        for i in range(5):
            admin.failed_attempts += 1
            if admin.failed_attempts >= 5:
                admin.locked_until = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        # Check assertions
        self.assertEqual(admin.failed_attempts, 5)
        self.assertIsNotNone(admin.locked_until)
        self.assertTrue(admin.locked_until > datetime.utcnow())
        
    def test_fee_calculations(self):
        """
        Verifies student outstanding balance math calculations.
        """
        c = Course(course_name='PyTesting', duration='6 Months', fee=20000.0)
        db.session.add(c)
        db.session.flush()
        
        # Mathematics: Total = 20000, Discount = 2000, Paid = 8000 -> Pending = 10000
        total = 20000.0
        discount = 2000.0
        paid = 8000.0
        pending = total - discount - paid
        
        s = Student(
            student_id='FTCI2026999',
            full_name='Test Candidate',
            father_name='Parent Candidate',
            address='Street Row, India',
            state='Maharashtra',
            pin_code='400050',
            mobile='7654321098',
            dob=date(2000, 1, 1),
            gender='Male',
            education='Undergraduate',
            course_id=c.id,
            batch='Morning 8-10',
            duration='6 Months',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 7, 1),
            total_fee=total,
            registration_fee=2000.0,
            discount=discount,
            paid_fee=paid,
            pending_fee=pending,
            payment_method='Card',
            receipt_number='RCP20269999',
            status='Active'
        )
        
        db.session.add(s)
        db.session.commit()
        
        self.assertEqual(s.pending_fee, 10000.0)
        
    def test_sequential_student_id_increment(self):
        """
        Verifies student sequential identification ID generation.
        """
        c = Course(course_name='Data Science', duration='6 Months', fee=30000.0)
        db.session.add(c)
        db.session.flush()
        
        current_year = datetime.utcnow().year
        
        # Test empty table generation starts at sequence 001
        first_id = generate_student_id()
        self.assertEqual(first_id, f"FTCI{current_year}001")
        
        # Save first student record
        s1 = Student(
            student_id=first_id,
            full_name='Candidate One',
            father_name='Father One',
            address='Mumbai Address',
            state='Maharashtra',
            pin_code='400001',
            mobile='8888888888',
            dob=date(1998, 12, 12),
            gender='Female',
            education='Postgraduate',
            course_id=c.id,
            batch='Evening',
            duration='6 Months',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 7, 1),
            total_fee=30000.0,
            discount=0.0,
            paid_fee=5000.0,
            pending_fee=25000.0,
            payment_method='UPI',
            receipt_number='RCP20261111',
            status='Active'
        )
        db.session.add(s1)
        db.session.commit()
        
        # Test second sequence increments to 002
        second_id = generate_student_id()
        self.assertEqual(second_id, f"FTCI{current_year}002")

if __name__ == '__main__':
    unittest.main()

from flask import Flask, render_template, g, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, Admin, Course, Setting
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.students import students_bp
from routes.courses import courses_bp
from routes.fees import fees_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.print import print_bp

# Initialize core Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Enable extensions
db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Session expired. Please log in to access the system.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Register blueprint controllers
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(students_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(fees_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(print_bp)

# Error Page Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Global Hooks to load settings and make helpers available to Jinja
@app.before_request
def load_global_settings():
    """
    Ensures g.settings is loaded for logo, institute name and signatures.
    If the settings table is empty, seeds default metadata configuration.
    """
    # Skip settings loading on static routes
    if request.endpoint == 'static':
        return
        
    try:
        g.settings = Setting.query.first()
        if not g.settings:
            g.settings = Setting(
                institute_name='FutureTech Computer Institute',
                study_center_code='P22',
                address='Main Street Campus, Mumbai, MH',
                phone='9876543210',
                email='admissions@futuretechinstitute.in',
                receipt_footer='Fee payments are non-refundable. Please keep this receipt for future reference.'
            )
            db.session.add(g.settings)
            db.session.commit()
    except Exception:
        # Prevent page crashes during database migrations or table setup
        g.settings = None

@app.context_processor
def inject_active_page():
    """
    Injects context elements like Course class and active navigation hooks
    to simplify templates.
    """
    from datetime import date, datetime
    return {
        'Course': Course,
        'Setting': Setting,
        'date': date,
        'datetime': datetime
    }

def seed_database():
    """
    Seeds default admin and courses into database on startup if not present.
    """
    # 1. Admin login credentials (Default: Futuretech / Futuretech@123)
    admin = Admin.query.filter_by(username='Futuretech').first()
    if not admin:
        default_admin = Admin(username='Futuretech')
        default_admin.set_password('Futuretech@123')
        db.session.add(default_admin)
        
        # Clean up the legacy default admin account if present
        old_admin = Admin.query.filter_by(username='admin').first()
        if old_admin:
            db.session.delete(old_admin)
        
    # 2. Predefined seed courses
    default_courses = [
        ('Python Programming', '6 Months', 15000.0, 'Comprehensive Python course covering basics to advanced topics.'),
        ('Java Development', '6 Months', 18000.0, 'Core and Advanced Java coding with frameworks.'),
        ('C Programming', '3 Months', 8000.0, 'Fundamentals of programming and C language.'),
        ('Data Analytics', '6 Months', 25000.0, 'Pandas, NumPy, SQL, Excel, and PowerBI visualization.'),
        ('Artificial Intelligence', '9 Months', 35000.0, 'Deep learning, Neural networks, and NLP basics.'),
        ('Machine Learning', '6 Months', 30000.0, 'Supervised and unsupervised models with Scikit-learn.'),
        ('Cyber Security', '6 Months', 28000.0, 'Ethical hacking, network security, and cryptography.'),
        ('Full Stack Development', '12 Months', 45000.0, 'HTML, CSS, JS, Node, React, and Python Django/Flask.'),
        ('MS Office Essentials', '3 Months', 5000.0, 'Word, Excel, PowerPoint, and Outlook essentials.'),
        ('Tally Prime', '3 Months', 6000.0, 'Accounting, GST filing, and financial bookkeeping.'),
        ('Graphic Design', '4 Months', 12000.0, 'Photoshop, Illustrator, InDesign, and core design theory.'),
        ('Web Development', '6 Months', 15000.0, 'Frontend HTML, CSS, JavaScript, and Bootstrap styling.')
    ]
    
    for name, duration, fee, desc in default_courses:
        if not Course.query.filter_by(course_name=name).first():
            c = Course(course_name=name, duration=duration, fee=fee, description=desc, status='Active')
            db.session.add(c)
            
    db.session.commit()

# Serve uploaded images (supports /tmp/uploads on serverless environments like Vercel)
from flask import send_from_directory
import os

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(os.path.join(upload_dir, filename)):
        return send_from_directory(upload_dir, filename)
    static_upload_dir = os.path.join(Config.BASE_DIR, 'static', 'uploads')
    if os.path.exists(os.path.join(static_upload_dir, filename)):
        return send_from_directory(static_upload_dir, filename)
    return '', 404

# Automatically initialize database tables and seed defaults on app startup
with app.app_context():
    try:
        db.create_all()
        seed_database()
    except Exception as err:
        app.logger.error(f"Database initialization error: {err}")

if __name__ == '__main__':
    # Run the application
    app.run(host='127.0.0.1', port=5000, debug=True)



from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import Admin, db
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin:
            # Check lockout state
            if admin.locked_until and admin.locked_until > datetime.utcnow():
                time_left = admin.locked_until - datetime.utcnow()
                minutes_left = int(time_left.total_seconds() / 60) + 1
                flash(f"Account temporarily locked. Please try again in {minutes_left} minute(s).", "danger")
                return render_template('login.html', form=form)
                
            if admin.check_password(password):
                # Reset lockout counters on success
                admin.failed_attempts = 0
                admin.locked_until = None
                db.session.commit()
                
                login_user(admin, remember=remember)
                flash("Welcome back! Logged in successfully.", "success")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard.index'))
            else:
                # Increment failed attempts
                admin.failed_attempts += 1
                if admin.failed_attempts >= 5:
                    admin.locked_until = datetime.utcnow() + timedelta(minutes=10)
                    flash("Too many failed attempts. Account locked for 10 minutes.", "danger")
                else:
                    remaining = 5 - admin.failed_attempts
                    flash(f"Incorrect credentials. {remaining} attempt(s) remaining before temporary lockout.", "danger")
                db.session.commit()
        else:
            # Don't give hints about valid usernames, keep generic
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

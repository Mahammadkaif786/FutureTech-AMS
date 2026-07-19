from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from models import Setting, db
from forms import SettingsForm
from utils import save_branding_file

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    # Fetch first settings row. If none exists, create with default seeding
    settings = Setting.query.first()
    if not settings:
        settings = Setting(
            institute_name='FutureTech Computer Institute',
            study_center_code='P22',
            address='Main Street Campus, Mumbai, MH',
            phone='9876543210',
            email='admissions@futuretechinstitute.in',
            receipt_footer='Fee payments are non-refundable. Please keep this receipt for future reference.'
        )
        db.session.add(settings)
        db.session.commit()
        
    form = SettingsForm()
    
    if request.method == 'GET':
        form.institute_name.data = settings.institute_name
        form.study_center_code.data = settings.study_center_code
        form.address.data = settings.address
        form.phone.data = settings.phone
        form.email.data = settings.email
        form.receipt_footer.data = settings.receipt_footer
        
    if form.validate_on_submit():
        # Photo handling: Logo
        if form.logo.data:
            logo_filename = save_branding_file(form.logo.data, current_app.config['UPLOAD_FOLDER'], settings.logo)
            settings.logo = logo_filename
            
        # Photo handling: Certificate signature
        if form.certificate_signature.data:
            sig_filename = save_branding_file(form.certificate_signature.data, current_app.config['UPLOAD_FOLDER'], settings.certificate_signature)
            settings.certificate_signature = sig_filename
            
        # Text fields updates
        settings.institute_name = form.institute_name.data.strip()
        settings.study_center_code = form.study_center_code.data.strip()
        settings.address = form.address.data.strip() if form.address.data else ''
        settings.phone = form.phone.data.strip() if form.phone.data else ''
        settings.email = form.email.data.strip() if form.email.data else ''
        settings.receipt_footer = form.receipt_footer.data.strip() if form.receipt_footer.data else ''
        
        db.session.commit()
        flash("Institute profile settings updated successfully!", "success")
        return redirect(url_for('settings.index'))
        
    return render_template('settings.html', form=form, settings=settings, active_page='settings')

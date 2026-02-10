"""
Dashboard Blueprint Routes
User dashboard and property management
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from core.data_manager import get_data_manager
from .forms import ProfileForm
import os
import uuid
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../../templates/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard homepage"""
    dm = get_data_manager()
    
    # Get user's properties
    user_properties = dm.find_many('properties', lambda p: p.get('user_id') == current_user.id)
    
    # Get statistics
    stats = {
        'total_properties': len(user_properties),
        'active_properties': len([p for p in user_properties if p.get('status') == 'active']),
        'pending_properties': len([p for p in user_properties if p.get('status') == 'pending']),
        'views_total': sum(p.get('views', 0) for p in user_properties),
        'with_tour': len([p for p in user_properties if p.get('tour', {}).get('scenes')])
    }
    
    return render_template('dashboard.html', stats=stats, properties=user_properties)


@dashboard_bp.route('/properties')
@login_required
def properties():
    """User's properties list"""
    dm = get_data_manager()
    user_properties = dm.find_many('properties', lambda p: p.get('user_id') == current_user.id)
    
    return render_template('properties_list.html', properties=user_properties)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm()
    dm = get_data_manager()
    
    # Get user's properties for stats
    user_properties = dm.find_many('properties', lambda p: p.get('user_id') == current_user.id)
    
    # Calculate statistics
    stats = {
        'total_properties': len(user_properties),
        'active_properties': len([p for p in user_properties if p.get('status') == 'active']),
        'with_tour': len([p for p in user_properties if p.get('tour', {}).get('scenes')]),
        'total_views': sum(p.get('views', 0) for p in user_properties)
    }
    
    if request.method == 'GET':
        # Pre-fill form with current user data
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.city.data = current_user.city
        form.profession.data = current_user.profession
    
    if form.validate_on_submit():
        user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
        
        if not user_data:
            flash('Kullanıcı bulunamadı', 'danger')
            return redirect(url_for('dashboard.profile'))
        
        # Update basic info
        user_data['name'] = form.name.data
        user_data['bio'] = form.bio.data or ''
        user_data['city'] = form.city.data or ''
        user_data['profession'] = form.profession.data or ''
        user_data['updated_at'] = datetime.now().isoformat()
        
        # Handle photo upload
        if form.photo.data:
            photo_file = form.photo.data
            if photo_file.filename:
                # Generate unique filename
                file_ext = os.path.splitext(secure_filename(photo_file.filename))[1]
                filename = f"{uuid.uuid4()}{file_ext}"
                
                # Create upload directory if not exists
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(upload_dir, filename)
                photo_file.save(filepath)
                
                # Delete old photo if exists
                if user_data.get('photo_url'):
                    old_photo = os.path.join(current_app.root_path, 'static', user_data['photo_url'].lstrip('/'))
                    if os.path.exists(old_photo):
                        try:
                            os.remove(old_photo)
                        except:
                            pass
                
                # Update photo URL
                user_data['photo_url'] = f"/static/uploads/profiles/{filename}"
        
        # Update password if provided
        if form.current_password.data:
            if not check_password_hash(user_data['password'], form.current_password.data):
                flash('Mevcut şifre yanlış', 'danger')
                return render_template('profile.html', form=form, stats=stats)
            
            if form.new_password.data:
                user_data['password'] = generate_password_hash(form.new_password.data)
                flash('Şifreniz güncellendi', 'success')
        
        # Save updates
        dm.update('users', lambda u: u['id'] == current_user.id, user_data)
        flash('Profiliniz güncellendi', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('profile.html', form=form, stats=stats)


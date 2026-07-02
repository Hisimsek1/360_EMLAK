"""
Dashboard Blueprint Routes
User dashboard and property management
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, session
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

    # Top 5 most viewed properties for chart
    top_properties = sorted(user_properties, key=lambda p: p.get('views', 0), reverse=True)[:5]
    chart_labels = [p['title'][:20] + ('…' if len(p['title']) > 20 else '') for p in top_properties]
    chart_views = [p.get('views', 0) for p in top_properties]

    # Inbox messages for this user
    all_data = dm.read_all()
    messages = [m for m in all_data.get('messages', []) if m.get('owner_id') == current_user.id]
    messages.sort(key=lambda m: m.get('created_at', ''), reverse=True)

    # Recently viewed properties from session
    recently_viewed_ids = session.get('recently_viewed', [])
    recently_viewed = []
    for pid in recently_viewed_ids[:5]:
        prop = dm.find_one('properties', lambda p, i=pid: p.get('id') == i)
        if prop and prop.get('status') == 'active':
            recently_viewed.append(prop)

    return render_template(
        'dashboard.html',
        stats=stats,
        properties=user_properties,
        chart_labels=chart_labels,
        chart_views=chart_views,
        messages=messages,
        recently_viewed=recently_viewed,
    )


@dashboard_bp.route('/properties')
@login_required
def properties():
    """User's properties list"""
    dm = get_data_manager()
    user_properties = dm.find_many('properties', lambda p: p.get('user_id') == current_user.id)
    
    return render_template('properties_list.html', properties=user_properties)


@dashboard_bp.route('/favorites')
@login_required
def favorites():
    """User's saved/favorite properties."""
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
    favorite_ids = user_data.get('favorites', []) if user_data else []

    favorite_properties = []
    for pid in favorite_ids:
        prop = dm.find_one('properties', lambda p, i=pid: p.get('id') == i)
        if prop:
            favorite_properties.append(prop)

    return render_template('favorites.html', properties=favorite_properties)


@dashboard_bp.route('/messages')
@login_required
def messages():
    """Inbox: contact messages received for the current user's listings."""
    dm = get_data_manager()
    all_data = dm.read_all()
    inbox = [m for m in all_data.get('messages', []) if m.get('owner_id') == current_user.id]
    inbox.sort(key=lambda m: m.get('created_at', ''), reverse=True)
    unread = sum(1 for m in inbox if not m.get('is_read'))

    return render_template('messages.html', messages=inbox, unread=unread)


@dashboard_bp.route('/messages/<msg_id>/read', methods=['POST'])
@login_required
def mark_message_read(msg_id):
    """Mark a single received message as read, then return to the inbox."""
    dm = get_data_manager()
    all_data = dm.read_all()
    changed = False
    for msg in all_data.get('messages', []):
        if msg.get('id') == msg_id and msg.get('owner_id') == current_user.id:
            if not msg.get('is_read'):
                msg['is_read'] = True
                changed = True
            break
    if changed:
        dm.write_all(all_data)
    return redirect(url_for('dashboard.messages'))


@dashboard_bp.route('/messages/read-all', methods=['POST'])
@login_required
def mark_all_messages_read():
    """Mark all of the current user's received messages as read."""
    dm = get_data_manager()
    all_data = dm.read_all()
    changed = False
    for msg in all_data.get('messages', []):
        if msg.get('owner_id') == current_user.id and not msg.get('is_read'):
            msg['is_read'] = True
            changed = True
    if changed:
        dm.write_all(all_data)
    flash('Tüm mesajlar okundu olarak işaretlendi.', 'success')
    return redirect(url_for('dashboard.messages'))


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
                        except OSError:
                            pass
                
                # Update photo URL
                user_data['photo_url'] = f"/static/uploads/profiles/{filename}"
        
        # Update password if provided
        if form.current_password.data:
            if not check_password_hash(user_data['password_hash'], form.current_password.data):
                flash('Mevcut şifre yanlış', 'danger')
                return render_template('profile.html', form=form, stats=stats)

            if form.new_password.data:
                user_data['password_hash'] = generate_password_hash(
                    form.new_password.data, method='pbkdf2:sha256'
                )
                flash('Şifreniz güncellendi', 'success')

        # Save updates
        dm.update_one('users', lambda u: u['id'] == current_user.id, user_data)
        flash('Profiliniz güncellendi', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('profile.html', form=form, stats=stats)


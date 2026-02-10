"""
Admin Routes
Super Admin panel for user and property management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from core.data_manager import get_data_manager

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')


def super_admin_required(f):
    """Decorator to require super admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@super_admin_required
def index():
    """Admin dashboard"""
    dm = get_data_manager()
    data = dm.read_all()
    
    # Statistics
    stats = {
        'total_users': len(data.get('users', [])),
        'total_properties': len(data.get('properties', [])),
        'active_properties': len([p for p in data.get('properties', []) if p.get('status') == 'active']),
        'agents': len([u for u in data.get('users', []) if u.get('role') == 'agent']),
    }
    
    return render_template('admin/index.html', stats=stats)


@admin_bp.route('/users')
@login_required
@super_admin_required
def users():
    """User management"""
    dm = get_data_manager()
    data = dm.read_all()
    users = data.get('users', [])
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<user_id>/role', methods=['POST'])
@login_required
@super_admin_required
def update_user_role(user_id):
    """Update user role"""
    new_role = request.form.get('role')
    
    if new_role not in ['user', 'agent', 'admin', 'super_admin']:
        return jsonify({'success': False, 'error': 'Geçersiz rol'}), 400
    
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u['id'] == user_id)
    
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404
    
    user_data['role'] = new_role
    user_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('users', lambda u: u['id'] == user_id, user_data)
    
    flash(f'Kullanıcı rolü {new_role} olarak güncellendi.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@login_required
@super_admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u['id'] == user_id)
    
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404
    
    user_data['is_active'] = not user_data.get('is_active', True)
    user_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('users', lambda u: u['id'] == user_id, user_data)
    
    status = 'aktif' if user_data['is_active'] else 'pasif'
    flash(f'Kullanıcı durumu {status} olarak güncellendi.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/properties')
@login_required
@super_admin_required
def properties():
    """Property management"""
    dm = get_data_manager()
    data = dm.read_all()
    properties = data.get('properties', [])
    users = data.get('users', [])
    
    # Create user lookup
    user_lookup = {u['id']: u['name'] for u in users}
    
    # Add user names to properties
    for prop in properties:
        prop['user_name'] = user_lookup.get(prop['user_id'], 'Bilinmeyen')
    
    return render_template('admin/properties.html', properties=properties)


@admin_bp.route('/properties/<property_id>/status', methods=['POST'])
@login_required
@super_admin_required
def update_property_status(property_id):
    """Update property status"""
    new_status = request.form.get('status')
    
    if new_status not in ['draft', 'pending', 'active', 'inactive']:
        return jsonify({'success': False, 'error': 'Geçersiz durum'}), 400
    
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
    
    if not property_data:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
    
    property_data['status'] = new_status
    property_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('properties', lambda p: p['id'] == property_id, property_data)
    
    flash(f'İlan durumu {new_status} olarak güncellendi.', 'success')
    return redirect(url_for('admin.properties'))


@admin_bp.route('/properties/<property_id>/assign-agent', methods=['POST'])
@login_required
@super_admin_required
def assign_agent(property_id):
    """Assign agent to property"""
    agent_id = request.form.get('agent_id')
    
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
    
    if not property_data:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
    
    # Verify agent exists and has agent role
    if agent_id:
        agent = dm.find_one('users', lambda u: u['id'] == agent_id)
        if not agent or agent.get('role') != 'agent':
            flash('Geçersiz emlakçı seçimi.', 'danger')
            return redirect(url_for('admin.properties'))
    
    property_data['agent_id'] = agent_id if agent_id else None
    property_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('properties', lambda p: p['id'] == property_id, property_data)
    
    flash('Emlakçı ataması güncellendi.', 'success')
    return redirect(url_for('admin.properties'))

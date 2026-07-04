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
    
    properties = data.get('properties', [])
    users = data.get('users', [])

    # Core stats
    stats = {
        'total_users': len(users),
        'total_properties': len(properties),
        'active_properties': len([p for p in properties if p.get('status') == 'active']),
        'agents': len([u for u in users if u.get('role') == 'agent']),
        'total_views': sum(p.get('views', 0) for p in properties),
        'with_tour': len([p for p in properties if p.get('tour', {}).get('scenes')]),
    }

    # Role distribution for pie chart
    from collections import Counter
    role_counts = Counter(u.get('role', 'user') for u in users)
    role_labels = list(role_counts.keys())
    role_data = list(role_counts.values())

    # Property status distribution
    status_counts = Counter(p.get('status', 'draft') for p in properties)
    status_labels = list(status_counts.keys())
    status_data = list(status_counts.values())

    # Top 5 cities by property count
    city_counts = Counter(p.get('city', 'Bilinmeyen') for p in properties)
    top_cities = city_counts.most_common(5)
    city_labels = [c[0] for c in top_cities]
    city_data = [c[1] for c in top_cities]

    return render_template(
        'admin/index.html',
        stats=stats,
        role_labels=role_labels,
        role_data=role_data,
        status_labels=status_labels,
        status_data=status_data,
        city_labels=city_labels,
        city_data=city_data,
    )


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
    user_data = dm.find_one('users', lambda u: u.get('id') == user_id)
    
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404
    
    user_data['role'] = new_role
    user_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('users', lambda u: u.get('id') == user_id, user_data)
    
    flash(f'Kullanıcı rolü {new_role} olarak güncellendi.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@login_required
@super_admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u.get('id') == user_id)
    
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404
    
    user_data['is_active'] = not user_data.get('is_active', True)
    user_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('users', lambda u: u.get('id') == user_id, user_data)
    
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
    property_data = dm.find_one('properties', lambda p: p.get('id') == property_id)
    
    if not property_data:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
    
    property_data['status'] = new_status
    property_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('properties', lambda p: p.get('id') == property_id, property_data)
    
    flash(f'İlan durumu {new_status} olarak güncellendi.', 'success')
    return redirect(url_for('admin.properties'))


@admin_bp.route('/reports')
@login_required
@super_admin_required
def reports():
    """View flagged property reports."""
    dm = get_data_manager()
    all_data = dm.read_all()
    all_reports = all_data.get('reports', [])
    all_reports.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return render_template('admin/reports.html', reports=all_reports)


@admin_bp.route('/reports/<report_id>/resolve', methods=['POST'])
@login_required
@super_admin_required
def resolve_report(report_id):
    """Mark a report as resolved or dismissed."""
    new_status = request.form.get('status', 'resolved')
    if new_status not in ('resolved', 'dismissed'):
        flash('Geçersiz durum.', 'danger')
        return redirect(url_for('admin.reports'))

    dm = get_data_manager()
    all_data = dm.read_all()
    for rep in all_data.get('reports', []):
        if rep.get('id') == report_id:
            rep['status'] = new_status
            rep['resolved_at'] = datetime.now().isoformat()
            dm.write_all(all_data)
            flash(f'Şikayet {new_status} olarak işaretlendi.', 'success')
            return redirect(url_for('admin.reports'))

    flash('Şikayet bulunamadı.', 'danger')
    return redirect(url_for('admin.reports'))


@admin_bp.route('/properties/<property_id>/assign-agent', methods=['POST'])
@login_required
@super_admin_required
def assign_agent(property_id):
    """Assign agent to property"""
    agent_id = request.form.get('agent_id')
    
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p.get('id') == property_id)
    
    if not property_data:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
    
    # Verify agent exists and has agent role
    if agent_id:
        agent = dm.find_one('users', lambda u: u.get('id') == agent_id)
        if not agent or agent.get('role') != 'agent':
            flash('Geçersiz emlakçı seçimi.', 'danger')
            return redirect(url_for('admin.properties'))
    
    property_data['agent_id'] = agent_id if agent_id else None
    property_data['updated_at'] = datetime.now().isoformat()
    
    dm.update_one('properties', lambda p: p.get('id') == property_id, property_data)
    
    flash('Emlakçı ataması güncellendi.', 'success')
    return redirect(url_for('admin.properties'))

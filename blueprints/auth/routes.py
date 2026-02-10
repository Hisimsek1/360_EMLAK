"""
Auth Blueprint Routes
Handles user registration, login, and logout
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

from blueprints.auth.forms import LoginForm, RegisterForm
from core.models import User
from core.data_manager import get_data_manager

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Create new user with hashed password
            user_data = User.create_new_user(
                email=form.email.data.lower().strip(),
                name=form.name.data.strip(),
                password=form.password.data,
                phone=form.phone.data.strip() if form.phone.data else '',
                role='user'  # Will be auto-upgraded to super_admin if email matches
            )
            
            # Save to database
            dm = get_data_manager()
            dm.insert_one('users', user_data)
            
            # Show success message
            if user_data['role'] == 'super_admin':
                flash('Hoş geldiniz! Süper Admin olarak kaydınız tamamlandı.', 'success')
            else:
                flash('Kayıt işleminiz başarıyla tamamlandı. Şimdi giriş yapabilirsiniz.', 'success')
            
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            flash(f'Kayıt sırasında bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        dm = get_data_manager()
        user_data = dm.find_one('users', lambda u: u['email'].lower() == form.email.data.lower().strip())
        
        if not user_data:
            flash('E-posta veya şifre hatalı.', 'danger')
            return render_template('login.html', form=form)
        
        # Create User object
        user = User(user_data)
        
        # Check if account is active
        if not user.is_active:
            flash('Hesabınız devre dışı bırakılmış. Lütfen yönetici ile iletişime geçin.', 'warning')
            return render_template('login.html', form=form)
        
        # Verify password
        if not user.check_password(form.password.data):
            flash('E-posta veya şifre hatalı.', 'danger')
            return render_template('login.html', form=form)
        
        # Update last login
        user.update_last_login()
        dm.update_one(
            'users',
            lambda u: u['id'] == user.id,
            {'last_login': user.last_login}
        )
        
        # Log user in
        login_user(user, remember=form.remember_me.data)
        
        # Show welcome message
        if user.is_super_admin():
            flash(f'Hoş geldiniz, {user.name}! (Süper Admin)', 'success')
        elif user.is_admin():
            flash(f'Hoş geldiniz, {user.name}! (Admin)', 'success')
        else:
            flash(f'Hoş geldiniz, {user.name}!', 'success')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('dashboard.index'))
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page - To be implemented"""
    return render_template('profile.html')

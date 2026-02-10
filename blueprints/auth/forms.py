"""
WTForms for Authentication
Login and Registration forms with validation
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, Regexp
)
from core.data_manager import get_data_manager


class LoginForm(FlaskForm):
    """User login form"""
    
    email = StringField(
        'E-posta',
        validators=[
            DataRequired(message='E-posta adresi gereklidir'),
            Email(message='Geçerli bir e-posta adresi giriniz')
        ],
        render_kw={'placeholder': 'ornek@email.com', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Şifre',
        validators=[
            DataRequired(message='Şifre gereklidir')
        ],
        render_kw={'placeholder': 'Şifrenizi giriniz', 'class': 'form-control'}
    )
    
    remember_me = BooleanField(
        'Beni Hatırla',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField('Giriş Yap', render_kw={'class': 'btn btn-primary w-100'})


class RegisterForm(FlaskForm):
    """User registration form"""
    
    name = StringField(
        'Ad Soyad',
        validators=[
            DataRequired(message='Ad soyad gereklidir'),
            Length(min=3, max=100, message='Ad soyad 3-100 karakter arasında olmalıdır')
        ],
        render_kw={'placeholder': 'Ad Soyad', 'class': 'form-control'}
    )
    
    email = StringField(
        'E-posta',
        validators=[
            DataRequired(message='E-posta adresi gereklidir'),
            Email(message='Geçerli bir e-posta adresi giriniz')
        ],
        render_kw={'placeholder': 'ornek@email.com', 'class': 'form-control'}
    )
    
    phone = StringField(
        'Telefon',
        validators=[
            Length(min=10, max=20, message='Geçerli bir telefon numarası giriniz')
        ],
        render_kw={'placeholder': '05XX XXX XX XX', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Şifre',
        validators=[
            DataRequired(message='Şifre gereklidir'),
            Length(min=6, max=100, message='Şifre en az 6 karakter olmalıdır')
        ],
        render_kw={'placeholder': 'En az 6 karakter', 'class': 'form-control'}
    )
    
    password_confirm = PasswordField(
        'Şifre Tekrar',
        validators=[
            DataRequired(message='Şifre tekrarı gereklidir'),
            EqualTo('password', message='Şifreler eşleşmiyor')
        ],
        render_kw={'placeholder': 'Şifrenizi tekrar giriniz', 'class': 'form-control'}
    )
    
    terms_accepted = BooleanField(
        'Kullanım koşullarını ve gizlilik politikasını kabul ediyorum',
        validators=[
            DataRequired(message='Kullanım koşullarını kabul etmelisiniz')
        ],
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField('Kayıt Ol', render_kw={'class': 'btn btn-primary w-100'})
    
    def validate_email(self, field):
        """Check if email already exists"""
        dm = get_data_manager()
        existing_user = dm.find_one('users', lambda u: u['email'].lower() == field.data.lower())
        
        if existing_user:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen farklı bir e-posta kullanın.')


class ChangePasswordForm(FlaskForm):
    """Change password form"""
    
    current_password = PasswordField(
        'Mevcut Şifre',
        validators=[
            DataRequired(message='Mevcut şifre gereklidir')
        ],
        render_kw={'placeholder': 'Mevcut şifreniz', 'class': 'form-control'}
    )
    
    new_password = PasswordField(
        'Yeni Şifre',
        validators=[
            DataRequired(message='Yeni şifre gereklidir'),
            Length(min=6, max=100, message='Şifre en az 6 karakter olmalıdır')
        ],
        render_kw={'placeholder': 'Yeni şifreniz', 'class': 'form-control'}
    )
    
    new_password_confirm = PasswordField(
        'Yeni Şifre Tekrar',
        validators=[
            DataRequired(message='Şifre tekrarı gereklidir'),
            EqualTo('new_password', message='Şifreler eşleşmiyor')
        ],
        render_kw={'placeholder': 'Yeni şifrenizi tekrar giriniz', 'class': 'form-control'}
    )
    
    submit = SubmitField('Şifreyi Değiştir', render_kw={'class': 'btn btn-primary'})

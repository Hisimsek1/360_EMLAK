"""
Dashboard Forms
Profile update and settings forms
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo


class ProfileForm(FlaskForm):
    """User profile update form"""
    name = StringField('Ad Soyad', validators=[
        DataRequired(message='Ad Soyad gereklidir'),
        Length(min=2, max=100, message='Ad Soyad 2-100 karakter arası olmalıdır')
    ])
    
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    
    bio = TextAreaField('Hakkımda', validators=[
        Optional(),
        Length(max=400, message='Hakkımda en fazla 400 karakter olabilir')
    ])
    
    city = StringField('Şehir', validators=[
        Optional(),
        Length(max=50, message='Şehir en fazla 50 karakter olabilir')
    ])
    
    profession = StringField('Meslek / Ünvan', validators=[
        Optional(),
        Length(max=100, message='Meslek en fazla 100 karakter olabilir')
    ])
    
    photo = FileField('Profil Fotoğrafı', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Sadece resim dosyaları yüklenebilir!')
    ])
    
    current_password = PasswordField('Mevcut Şifre', validators=[
        Optional()
    ])
    
    new_password = PasswordField('Yeni Şifre', validators=[
        Optional(),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    
    confirm_password = PasswordField('Yeni Şifre Tekrar', validators=[
        Optional(),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])
    
    submit = SubmitField('Güncelle')

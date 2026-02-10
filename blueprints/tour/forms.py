"""
Tour Forms
Forms for property and virtual tour management
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PropertyForm(FlaskForm):
    """Property creation/edit form"""
    
    title = StringField(
        'İlan Başlığı',
        validators=[
            DataRequired(message='Başlık gereklidir'),
            Length(min=10, max=200, message='Başlık 10-200 karakter arasında olmalıdır')
        ],
        render_kw={'placeholder': 'Örn: Merkezi Konumda Satılık 3+1 Daire', 'class': 'form-control'}
    )
    
    description = TextAreaField(
        'Açıklama',
        validators=[
            DataRequired(message='Açıklama gereklidir'),
            Length(min=50, max=5000, message='Açıklama 50-5000 karakter arasında olmalıdır')
        ],
        render_kw={'placeholder': 'İlan detaylarını giriniz...', 'class': 'form-control', 'rows': 6}
    )
    
    category = SelectField(
        'Kategori',
        validators=[DataRequired(message='Kategori seçimi gereklidir')],
        choices=[],  # Will be populated dynamically
        render_kw={'class': 'form-select'}
    )
    
    listing_type = SelectField(
        'İlan Tipi',
        validators=[DataRequired(message='İlan tipi seçimi gereklidir')],
        choices=[
            ('sale', 'Satılık'),
            ('rent', 'Kiralık')
        ],
        render_kw={'class': 'form-select'}
    )
    
    price = IntegerField(
        'Fiyat (₺)',
        validators=[
            DataRequired(message='Fiyat gereklidir'),
            NumberRange(min=1, message='Geçerli bir fiyat giriniz')
        ],
        render_kw={'placeholder': '0', 'class': 'form-control'}
    )
    
    city = SelectField(
        'Şehir',
        validators=[DataRequired(message='Şehir seçimi gereklidir')],
        choices=[],  # Will be populated dynamically
        render_kw={'class': 'form-select'}
    )
    
    district = StringField(
        'İlçe',
        validators=[
            DataRequired(message='İlçe gereklidir'),
            Length(max=100)
        ],
        render_kw={'placeholder': 'İlçe', 'class': 'form-control'}
    )
    
    address = TextAreaField(
        'Adres',
        validators=[
            DataRequired(message='Adres gereklidir'),
            Length(max=500)
        ],
        render_kw={'placeholder': 'Tam adres...', 'class': 'form-control', 'rows': 3}
    )
    
    # Property Details
    area = IntegerField(
        'Alan (m²)',
        validators=[
            DataRequired(message='Alan gereklidir'),
            NumberRange(min=1, max=100000, message='Geçerli bir alan giriniz')
        ],
        render_kw={'placeholder': '0', 'class': 'form-control'}
    )
    
    rooms = StringField(
        'Oda Sayısı',
        validators=[Length(max=20)],
        render_kw={'placeholder': 'Örn: 3+1', 'class': 'form-control'}
    )
    
    floor = StringField(
        'Kat',
        validators=[Length(max=20)],
        render_kw={'placeholder': 'Örn: 5. Kat', 'class': 'form-control'}
    )
    
    building_age = IntegerField(
        'Bina Yaşı',
        validators=[NumberRange(min=0, max=200, message='Geçerli bir yaş giriniz')],
        render_kw={'placeholder': '0', 'class': 'form-control'}
    )
    
    # Normal photos (multiple upload)
    images = MultipleFileField(
        'Fotoğraflar (En az 3, en fazla 20)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece JPG, JPEG ve PNG dosyaları yüklenebilir')
        ],
        render_kw={'class': 'form-control', 'accept': 'image/jpeg,image/jpg,image/png', 'multiple': True}
    )
    
    submit = SubmitField('Kaydet ve Devam Et', render_kw={'class': 'btn btn-primary'})


class SceneForm(FlaskForm):
    """360 Scene upload form"""
    
    name = StringField(
        'Sahne Adı',
        validators=[
            DataRequired(message='Sahne adı gereklidir'),
            Length(min=3, max=100, message='Sahne adı 3-100 karakter arasında olmalıdır')
        ],
        render_kw={'placeholder': 'Örn: Salon, Yatak Odası, Mutfak', 'class': 'form-control'}
    )
    
    image = FileField(
        '360° Fotoğraf',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece JPG, JPEG ve PNG dosyaları yüklenebilir')
        ],
        render_kw={'class': 'form-control', 'accept': 'image/jpeg,image/jpg,image/png'}
    )
    
    submit = SubmitField('Sahne Ekle', render_kw={'class': 'btn btn-primary'})

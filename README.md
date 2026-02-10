# 🏠 360 Emlak - Profesyonel SaaS Emlak Platformu

Modern, güvenli ve kullanıcı dostu emlak alım-satım platformu. 360° sanal tur teknolojisi ile gayrimenkulleri gerçekçi bir şekilde görüntüleme imkanı sunar.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

## 🚀 Özellikler

### ✅ **Tamamlanan Özellikler**

- 🏗️ **Modern Mimari**: Factory Pattern ile Flask uygulama yapısı
- 🔐 **Güvenli Kimlik Doğrulama**: Flask-Login + CSRF koruması
- 👤 **Kapsamlı Profil Sistemi**: Bio, fotoğraf, şehir, meslek bilgileri
- 📊 **Professional Dashboard**: Navy temalı, istatistikli kullanıcı paneli  
- 🎨 **Modern UI/UX**: Bootstrap 5 + Navy gradient tasarım sistemi
- 🌐 **360° Sanal Turlar**: Pannellum.js ile immersive görüntüleme
- 📱 **Responsive Design**: Mobil ve desktop uyumlu
- 🔧 **Admin Panel**: Super admin yönetim sistemi
- 🗂️ **JSON Database**: Thread-safe, kolay yönetim
- 📁 **Dosya Yükleme**: Güvenli profil fotoğrafı ve ilan görseli yükleme
- 🛡️ **Production Ready**: Gunicorn + environment configuration

### 🎨 **Tasarım Sistemi**

- **Ana Renk Paleti**: Navy Blue (#1E3A8A), Royal Blue (#2563EB)
- **Tasarım Dili**: Professional SaaS, minimalist, güven veren
- **Komponentler**: 
  - Gradient stat kartları (5 farklı tema)
  - Interactive dashboard
  - Professional profil sistemi
  - Modern form elements
  - Responsive navigation

## 📁 Proje Yapısı

```
360EV/
├── 📄 app.py                    # Flask factory pattern uygulama
├── ⚙️ config.py                 # Çoklu ortam konfigürasyonu
├── 🚀 wsgi.py                   # Production WSGI entry point
├── 📋 requirements.txt          # Python dependencies
├── 🧪 test_app.py               # Test suite (pytest)
├── 📝 README.md                 # Bu dosya
├── 🔄 .gitignore               # Git ignore kuralları
├── 🌐 .env.example             # Environment template
├── 📊 UPGRADE_PLAN.md          # Geliştirme planı
├── 📊 DASHBOARD_DESIGN.md      # Dashboard tasarım rehberi
├── 
├── 📂 blueprints/              # Flask blueprints (modüler yapı)
│   ├── 🏠 main/               # Ana sayfalar (anasayfa, hakkımızda, iletişim)
│   ├── 🔐 auth/               # Kimlik doğrulama (giriş, kayıt, çıkış)
│   ├── 📊 dashboard/          # Kullanıcı paneli ve profil yönetimi
│   ├── 🏢 property/           # İlan listeleme ve detayları
│   ├── 🎯 tour/               # 360° tur oluşturma ve düzenleme
│   └── ⚡ admin/              # Admin panel (super admin only)
├── 
├── 🔧 core/                   # Çekirdek sistemler
│   ├── 🗄️ database.py         # JSON database operations
│   ├── 📊 data_manager.py     # Data management layer
│   ├── 👤 models.py           # User ve diğer modeller
│   └── 🛠️ utils.py            # Yardımcı fonksiyonlar
├── 
├── 🎨 static/                 # Statik dosyalar
│   ├── 💄 css/style.css       # Custom CSS + navbar styles
│   ├── ⚡ js/editor.js       # Tour editor JavaScript
│   ├── 🖼️ images/            # Logo ve genel görseller
│   └── 📁 uploads/           # Kullanıcı yüklemeleri
│       ├── 👤 profiles/      # Profil fotoğrafları
│       ├── 🏠 properties/    # İlan görselleri
│       └── 🎯 tours/         # 360° tur görselleri
├── 
├── 🎭 templates/              # Jinja2 HTML şablonları
│   ├── 🎯 base.html          # Temel şablon (navbar, footer)
│   ├── 🏠 main/              # Ana sayfa şablonları
│   ├── 🔐 auth/              # Authentication templates
│   ├── 📊 dashboard/         # Dashboard ve profil templates
│   ├── 🏢 property/          # İlan templates
│   ├── 🎯 tour/              # 360° tour templates
│   ├── ⚡ admin/             # Admin panel templates
│   └── ❌ errors/            # Hata sayfaları (404, 500, vb.)
├── 
├── 💾 data/                   # JSON veritabanı
│   ├── 🗄️ data.json          # Ana veri dosyası
│   └── 🔄 backups/          # Otomatik backup dosyaları
└── 
└── 📋 logs/                   # Uygulama logları
    └── 📝 app.log
```

## 🛠️ Kurulum ve Çalıştırma

### 1️⃣ Projeyi İndirin

```bash
cd 360EV
```

### 2️⃣ Virtual Environment

```powershell
# Windows PowerShell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Configuration

`.env` dosyası oluşturun:

```env
# Development
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-2024

# Production (örnek)
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here
```

### 5️⃣ Uygulamayı Başlatın

**Development:**
```bash
python app.py
```

**Production:**
```bash
gunicorn wsgi:app -b 0.0.0.0:5000 -w 4
```

🌐 **Uygulama `http://localhost:5000` adresinde çalışacaktır.**

## 🧪 Test

```bash
# Test suite çalıştır
python -m pytest test_app.py -v

# Coverage ile
pip install pytest-cov
python -m pytest test_app.py --cov=. --cov-report=html
```

## 👤 Kullanıcı Rolleri

| Rol | Açıklama | Yetkiler |
|-----|----------|----------|
| `user` | Normal kullanıcı | İlan oluşturma, profil düzenleme |
| `agent` | Emlak danışmanı | Gelişmiş ilan yönetimi |
| `admin` | Yönetici | Kullanıcı yönetimi, ilan moderasyonu |
| `super_admin` | Süper yönetici | Tüm sistem yönetimi |

## ⚙️ Konfigürasyon

### Environment Types

```python
# Development
DEBUG = True
SESSION_COOKIE_SECURE = False

# Production  
DEBUG = False
SESSION_COOKIE_SECURE = True
SECRET_KEY = environ.get('SECRET_KEY')  # Required!

# Testing
TESTING = True
WTF_CSRF_ENABLED = False
```

### File Upload

```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads'
```

## 🗄️ Database Structure

JSON tabanlı dosya veritabanı:

```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com", 
      "name": "Kullanıcı Adı",
      "role": "user|agent|admin|super_admin",
      "bio": "Hakkımda bilgisi",
      "city": "Şehir",
      "profession": "Meslek",
      "photo_url": "/static/uploads/profiles/...",
      "password_hash": "pbkdf2:sha256:...",
      "created_at": "2026-02-10T...",
      "is_active": true
    }
  ],
  "properties": [
    {
      "id": "uuid",
      "user_id": "uuid", 
      "title": "İlan Başlığı",
      "description": "Açıklama",
      "price": 1500000,
      "city": "Bursa",
      "district": "Yıldırım",
      "category": "konut|ticari",
      "listing_type": "sale|rent", 
      "status": "active|pending|inactive",
      "images": ["image1.jpg", "image2.jpg"],
      "tour": {
        "scenes": [...]  # 360° tur sahneleri
      },
      "views": 0,
      "created_at": "2026-02-10T..."
    }
  ],
  "pages": [...],      # Statik sayfalar (hakkımızda, vs.)
  "settings": {...},   # Site ayarları  
  "categories": [...], # İlan kategorileri
  "cities": [...]      # Şehir listesi
}
```

## 🔐 Güvenlik

### Implemented Security Features

✅ **CSRF Protection**: WTF-CSRF ile form koruması  
✅ **Password Hashing**: pbkdf2:sha256 ile güvenli hash  
✅ **Session Security**: HttpOnly, SameSite cookies  
✅ **File Upload Validation**: Type ve size kontrolü  
✅ **XSS Prevention**: Template auto-escaping  
✅ **Authentication**: Flask-Login session management  
✅ **Role-based Access**: Decorator'lar ile yetkilendirme  

### Security Best Practices

```python
# Production'da mutlaka ayarlayın
SECRET_KEY = strong-random-key
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True 
SESSION_COOKIE_SAMESITE = 'Lax'

# File upload güvenliği
MAX_CONTENT_LENGTH = 16MB
ALLOWED_EXTENSIONS = image_files_only
```

## 📊 Dashboard Features

### Kullanıcı Dashboard
- **İstatistik Kartları**: 5 farklı metrik (Toplam, Aktif, Bekleyen, Görüntülenme, 360°)
- **Navy Gradient Tema**: Professional SaaS tasarımı
- **Quick Actions**: Hızlı işlem butonları
- **Property Table**: Son ilanlar tablosu
- **Responsive Design**: Mobil uyumlu card layout

### Profil Sistemi  
- **Profil Fotoğrafı**: Upload ve önizleme
- **Bio**: 400 karakter kişisel tanıtım
- **Location**: Şehir bilgisi
- **Profession**: Meslek/ünvan
- **Statistics**: Kişisel ilan istatistikleri
- **Verification Badge**: Profil doğrulama rozeti

## 🎨 UI/UX Design System

### Colors (Navy Theme)
```css
--primary-navy: #1E3A8A     /* Ana lacivert */
--royal-blue: #2563EB       /* Royal mavi */ 
--success-teal: #0D9488     /* Başarı yeşili */
--warning-amber: #D97706    /* Uyarı turuncusu */
--info-indigo: #4F46E5      /* Bilgi indigo */
--purple: #7C3AED           /* Vurgu moru */
```

### Components
- **Stat Cards**: Gradient borders, hover effects
- **Buttons**: Navy gradient, transform animations
- **Forms**: Rounded inputs, focus states  
- **Navigation**: Sticky header, dropdown menus
- **Tables**: Gradient headers, hover rows
- **Badges**: Colorful role indicators

## 📈 Performance

### Optimizations
✅ **Static File Caching**: Browser cache headers  
✅ **Image Compression**: PIL ile otomatik resize  
✅ **JSON Database**: Thread-safe file locking  
✅ **Lazy Loading**: Template-level lazy loading  
✅ **CDN Assets**: Bootstrap, Font Awesome CDN  

### Monitoring
- **Logging**: File-based log system
- **Error Tracking**: Custom error pages
- **Performance Metrics**: Response time tracking (planned)

## 🚧 Roadmap & TODO

### 🎯 **Kısa Vadeli (Q1 2026)**
- [ ] Real-time notifications
- [ ] Advanced search filters  
- [ ] Map integration (Google Maps)
- [ ] WhatsApp integration
- [ ] Email notifications
- [ ] Backup automation

### 🔮 **Uzun Vadeli (Q2-Q3 2026)**  
- [ ] RESTful API
- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Advanced SEO optimization

### 💡 **Geliştirilmekte**
- [x] ✅ Dashboard redesign (Navy theme)
- [x] ✅ Profile system with photos
- [x] ✅ Admin panel foundation  
- [x] ✅ 360° tour system
- [ ] 🔄 Advanced property filters
- [ ] 🔄 SEO & social media integration

## 🤝 Contributing

Bu proje aktif geliştirme aşamasında. Contributions welcome!

### Development Setup
```bash
# Development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -v

# Code formatting (planned)
pip install black flake8
black . && flake8 .
```

## 📄 License

Bu proje özel bir SaaS platformudur. Tüm hakları saklıdır.

## 📞 İletişim & Support

- 📧 **E-posta**: info@360emlak.com  
- 📱 **Telefon**: +90 (212) 123 45 67
- 🌐 **Website**: [360emlak.com](http://localhost:5000)  
- 💼 **LinkedIn**: 360 Emlak Platform

---

<div align="center">

**🏠 360 Emlak** - *Geleceğin Gayrimenkul Platformu*

*Modern • Güvenli • Kullanıcı Dostu*

</div>
# 360 Emlak - Dashboard Tasarım Sistemi (Navy Edition)

## 🎨 Tasarım Felsefesi

**Lacivert tonlarıyla zenginleştirilmiş, profesyonel SaaS dashboard.** Canlı ama kurumsal, zengin ama abartısız, güven veren ama modern bir tasarım dili.

## 🎯 Renk Paleti

### Lacivert & Navy Tonları (Ana Palet)
```css
--dashboard-navy-primary: #1E3A8A      /* Ana Lacivert - Dominant color */
--dashboard-navy-dark: #1E293B         /* Koyu Navy - Sidebar background */
--dashboard-navy-medium: #334155       /* Orta Ton Navy */
--dashboard-royal-blue: #2563EB        /* Royal Blue - Aktif durumlar */
--dashboard-sky-blue: #3B82F6          /* Sky Blue - Hover, ikonlar */
--dashboard-indigo: #4F46E5            /* Indigo - Gradientler */
```

### Renkli Aksan Tonları
```css
--dashboard-teal: #0D9488              /* Teal - Success başlangıç */
--dashboard-emerald: #059669           /* Emerald - Success bitiş */
--dashboard-amber: #D97706             /* Amber - Warning */
--dashboard-purple: #7C3AED            /* Purple - Özel metrikler */
```

### Nötr & Background Tonları
```css
--dashboard-neutral-50: #F8FAFC        /* Ana arka plan */
--dashboard-neutral-100: #F1F5F9       /* Kartlar, hover */
--dashboard-neutral-200: #E2E8F0       /* Kenarlıklar */
--dashboard-neutral-700: #334155       /* Body text */
--dashboard-neutral-900: #0F172A       /* Başlıklar, koyu sidebar */
```

## 📐 Tasarım Tokenları

### Spacing
- Küçük: 0.5rem - 0.875rem
- Orta: 1rem - 1.5rem
- Büyük: 1.75rem - 2rem

### Border Radius
- Primary: 8px (orta yuvarlaklık)
- Kartlar: 8px
- Butonlar: 6-8px
- Badge'ler: 6px
- Avatar: 50% (tam yuvarlak)

### Gölgeler (Layered Depth)
```css
--dashboard-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12)
--dashboard-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--dashboard-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
```

## 🔤 Typography

### Font Stack
```css
font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

### Font Weights
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800 (sayılar için)

### Font Sizes
- Başlıklar (h3): 1.5rem (24px)
- Alt Başlıklar (h5): 1.0625rem (17px)
- Body: 0.9375rem (15px)
- Small: 0.875rem (14px)
- Tiny: 0.75rem (12px)

## 📊 Bileşenler

### 1. Sidebar - Navy Gradient

**Özellikler:**
- Background: Navy gradient (koyu → daha koyu)
- Beyaz text & ikonlar
- Avatar: 72px, Royal Blue gradient, beyaz border
- Nav Items:
  - 3px sol border (transparent → active)
  - Hover: Beyaz overlay
  - Active: Gradient overlay + Royal Blue border

**Renkler:**
```css
background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%)
border: 1px solid rgba(255,255,255,0.1)
```

### 2. Stat Kartları - Rich Gradients

**Özellikler:**
- Beyaz background
- Üst: 4px gradient border (statüye göre)
- İkon: 52x52px, gradient background, gölge
- Sayılar: 2.25rem, extrabold, gradient text
- Label: Uppercase, letter-spacing
- Hover: Yukarı kayma + büyük gölge

**Varyantlar:**
```css
/* Default - Navy Blue */
background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)

/* Success - Teal/Emerald */
background: linear-gradient(135deg, #0D9488 0%, #059669 100%)

/* Warning - Orange/Amber */
background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%)

/* Purple - Violet */
background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)

/* Info - Sky/Indigo */
background: linear-gradient(135deg, #3B82F6 0%, #4F46E5 100%)
```

### 3. Quick Action Buttons

**Primary:**
```css
background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)
color: white
box-shadow: 0 4px 15px rgba(30, 58, 138, 0.4)

/* Hover */
background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%)
box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5)
```

**Secondary:**
```css
background: white
border: 2px solid #E2E8F0

/* Hover */
border-color: #2563EB
background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(79, 70, 229, 0.05) 100%)
```

### 4. Tablo (Son İlanlar) - Rich Header

**Header:**
```css
background: linear-gradient(135deg, #1E293B 0%, #1E3A8A 100%)
color: white
font-weight: 700
text-transform: uppercase
letter-spacing: 0.05em
```

**Rows:**
```css
/* Hover */
background: linear-gradient(90deg, rgba(37, 99, 235, 0.03) 0%, transparent 100%)
```

### 5. Badge'ler - Rich Gradients

```css
/* Aktif */
background: linear-gradient(135deg, #0D9488 0%, #059669 100%)
color: white
box-shadow: 0 2px 6px rgba(13, 148, 136, 0.3)

/* Bekleyen */
background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%)
color: white
box-shadow: 0 2px 6px rgba(217, 119, 6, 0.3)

/* Pasif */
background: linear-gradient(135deg, #64748B 0%, #475569 100%)
color: white
box-shadow: 0 2px 6px rgba(100, 116, 139, 0.3)
```

## 🎭 Özel Efektler

### Gradient Text (Sayılar)
```css
background: linear-gradient(135deg, #1E293B 0%, #1E3A8A 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

### Hover Transformations
```css
/* Kartlar */
transform: translateY(-4px)
box-shadow: var(--dashboard-shadow-lg)

/* Butonlar */
transform: translateY(-3px)
box-shadow: 0 6px 20px rgba(...)
```

## 📱 Responsive Breakpoints

```css
/* Tablet */
@media (max-width: 991.98px)
  - Sidebar: Sticky → Relative
  - Stat Cards: 2 columns

/* Mobile */
@media (max-width: 767.98px)
  - Stat Cards: 1 column
  - Tablo: Kart görünümü
  - Quick Actions: Full width
```

## ✨ Animasyonlar

```css
transition: all 0.3s ease  /* Default */
```

**Hover Efektleri:**
- Scale: transform: scale(1.1) (ikonlar)
- Translate: translateY(-2px to -4px) (kartlar)
- Shadow: Smooth artış
- Gradient: Renk geçişi
- Border: Renk değişimi

## 🎯 UX Prensipleri

1. **Hiyerarşi**: Gradient sayılar, bold başlıklar
2. **Depth**: Layered gölgeler, gradient backgrounds
3. **Vibrance**: Zengin renkler ama profesyonel
4. **Motion**: Yumuşak, 0.3s geçişler
5. **Contrast**: Navy üzerine beyaz, beyaz üzerine navy
6. **Trust**: Kurumsal lacivert palet

## 🚀 Kullanım Örnekleri

### Stat Card HTML (Success Variant)
```html
<div class="stat-card success">
    <div class="stat-icon">
        <i class="fas fa-check-circle"></i>
    </div>
    <div class="stat-value">42</div>
    <div class="stat-label">Aktif İlan</div>
</div>
```

### Primary Button
```html
<a href="#" class="quick-action-btn primary">
    <i class="fas fa-plus-circle"></i>
    <span>Yeni İlan Ekle</span>
</a>
```

### Nav Link (Active)
```html
<a href="#" class="nav-link active">
    <i class="fas fa-tachometer-alt"></i> Dashboard
</a>
```

## 📝 Değişiklik Notu

### v2.1 - Navy Edition (2026-02-10)

**Önceki Versiyon Sorunları:**
- ❌ Çok sade, renksiz
- ❌ Minimal ama sıkıcı
- ❌ Kurumsal ama cansız

**Yeni Versiyon Çözümleri:**
- ✅ Lacivert gradient sidebar
- ✅ Zengin renkli stat kartları (5 farklı gradient)
- ✅ Gradient text sayılar
- ✅ Rich table header (navy gradient)
- ✅ Colorful badges (gradient + shadow)
- ✅ Vibrant hover efektleri
- ✅ Layered shadow system
- ✅ Avatar ile border + shadow
- ✅ Daha büyük ikonlar (52px)
- ✅ Daha bold sayılar (font-weight: 800)

**Korunan Özellikler:**
- ✅ Profesyonel ve kurumsal hava
- ✅ Güven veren tasarım
- ✅ Enterprise SaaS kalitesi
- ✅ Responsive yapı
- ✅ Ana sayfa değişmedi

## 🎨 Renk Karşılaştırma

| Element | Önceki | Yeni |
|---------|--------|------|
| Sidebar | Beyaz + border | Navy gradient + gölge |
| Stat Kartlar | Beyaz + sol border | Beyaz + üst gradient border |
| İkonlar | Soft bg + color | Gradient bg + shadow |
| Sayılar | Solid color | Gradient text |
| Badges | Soft bg | Gradient + shadow |
| Table Header | Açık gri | Navy gradient |
| Avatar | Basic gradient | Gradient + border + shadow |

---

**360 Emlak** - Profesyonel SaaS Emlak Platformu (Navy Edition)

*"Lacivert tonlarının gücü, profesyonelliğin imajı."*

"""
Main Blueprint Routes
Handles homepage, static pages (about, privacy, terms, contact)
"""
from flask import Blueprint, render_template, request
from core.database import get_page
from core.data_manager import get_data_manager

main_bp = Blueprint('main', __name__, template_folder='../../templates/main')

# Turkish Cities
CITIES = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya",
          "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik",
          "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum",
          "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir",
          "Gaziantep", "Giresun", "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "İstanbul",
          "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis",
          "Kırıkkale", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
          "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize",
          "Sakarya", "Samsun", "Şanlıurfa", "Siirt", "Sinop", "Sivas", "Şırnak", "Tekirdağ",
          "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"]


@main_bp.route('/')
def index():
    """Homepage with property listing and filters"""
    dm = get_data_manager()
    
    # Get filters from request
    filters = {
        'listing_type': request.args.get('listing_type'),
        'category': request.args.get('category'),
        'city': request.args.get('city'),
        'district': request.args.get('district'),
        'min_price': request.args.get('min_price', type=int),
        'max_price': request.args.get('max_price', type=int),
        'min_area': request.args.get('min_area', type=int),
        'max_area': request.args.get('max_area', type=int),
        'rooms': request.args.get('rooms'),
        'with_tour': request.args.get('with_tour') == 'on'
    }
    
    # Get all active properties
    all_properties = dm.find_many('properties', lambda p: p.get('status') == 'active')
    
    # Apply filters
    filtered_properties = []
    for prop in all_properties:
        # Check each filter
        if filters['listing_type'] and prop.get('listing_type') != filters['listing_type']:
            continue
        
        if filters['category'] and prop.get('category') != filters['category']:
            continue
        
        if filters['city'] and prop.get('city') != filters['city']:
            continue
        
        if filters['district'] and prop.get('district') != filters['district']:
            continue
        
        if filters['min_price'] and prop.get('price', 0) < filters['min_price']:
            continue
        
        if filters['max_price'] and prop.get('price', 0) > filters['max_price']:
            continue
        
        if filters['min_area'] and prop.get('area', 0) < filters['min_area']:
            continue
        
        if filters['max_area'] and prop.get('area', 0) > filters['max_area']:
            continue
        
        if filters['rooms'] and prop.get('rooms') != filters['rooms']:
            continue
        
        if filters['with_tour'] and not prop.get('tour', {}).get('scenes'):
            continue
        
        filtered_properties.append(prop)
    
    # Sort
    sort_by = request.args.get('sort', 'date_desc')
    if sort_by == 'price_asc':
        filtered_properties.sort(key=lambda p: p.get('price', 0))
    elif sort_by == 'price_desc':
        filtered_properties.sort(key=lambda p: p.get('price', 0), reverse=True)
    elif sort_by == 'area_desc':
        filtered_properties.sort(key=lambda p: p.get('area', 0), reverse=True)
    else:  # date_desc
        filtered_properties.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    
    # Get statistics
    all_users = dm.find_many('users', lambda u: True)
    stats = {
        'total_properties': len(all_properties),
        'with_tour': len([p for p in all_properties if p.get('tour', {}).get('scenes')]),
        'total_users': len(all_users),
        'total_cities': len(set(p.get('city') for p in all_properties if p.get('city')))
    }
    
    return render_template('index.html', 
                         properties=filtered_properties, 
                         filters=filters,
                         cities=CITIES,
                         stats=stats)


@main_bp.route('/page/<slug>')
def page(slug):
    """Display static pages"""
    page_data = get_page(slug)
    if not page_data:
        return render_template('errors/404.html'), 404
    
    return render_template('page.html', page=page_data)


@main_bp.route('/about')
def about():
    """About page"""
    page_data = get_page('hakkimizda')
    if not page_data:
        page_data = {
            'title': 'Hakkımızda',
            'content': '''
                <h2>360 Emlak Platformu</h2>
                <p class="lead">Modern emlak çözümleri için profesyonel platformunuz.</p>
                
                <h3>Misyonumuz</h3>
                <p>360 Emlak olarak, emlak sektöründe teknoloji ve yeniliği bir araya getirerek, 
                   alıcılar ve satıcılar için en iyi deneyimi sunmayı hedefliyoruz.</p>
                
                <h3>360° Sanal Tur Teknolojisi</h3>
                <p>Platformumuzun en önemli özelliği, ilanları 360 derece sanal tur ile görüntüleme imkanıdır. 
                   Bu sayede, potansiyel alıcılar evleri sanki oradaymış gibi gezebilir.</p>
                
                <h3>Özelliklerimiz</h3>
                <ul>
                    <li>360° Sanal Tur ile emlak görüntüleme</li>
                    <li>Gelişmiş arama ve filtreleme</li>
                    <li>Kullanıcı dostu arayüz</li>
                    <li>Mobil uyumlu tasarım</li>
                    <li>Güvenli ve hızlı platform</li>
                </ul>
            '''
        }
    return render_template('page.html', page=page_data)


@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    page_data = get_page('gizlilik-politikasi')
    if not page_data:
        page_data = {
            'title': 'Gizlilik Politikası',
            'content': '''
                <h2>Gizlilik Politikası</h2>
                <p>360 Emlak olarak, kullanıcılarımızın gizliliğine önem veriyoruz.</p>
                
                <h3>Toplanan Bilgiler</h3>
                <p>Platformumuzu kullanırken, aşağıdaki bilgiler toplanabilir:</p>
                <ul>
                    <li>İsim, e-posta ve telefon bilgileri</li>
                    <li>İlan bilgileri ve görseller</li>
                    <li>Platform kullanım istatistikleri</li>
                </ul>
                
                <h3>Bilgilerin Kullanımı</h3>
                <p>Toplanan bilgiler yalnızca platform hizmetlerini sağlamak için kullanılır.</p>
            '''
        }
    return render_template('page.html', page=page_data)


@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    page_data = get_page('kullanim-kosullari')
    if not page_data:
        page_data = {
            'title': 'Kullanım Koşulları',
            'content': '''
                <h2>Kullanım Koşulları</h2>
                <p>360 Emlak platformunu kullanarak aşağıdaki koşulları kabul etmiş sayılırsınız.</p>
                
                <h3>Genel Kurallar</h3>
                <ul>
                    <li>Platform hizmetlerini yasalara uygun şekilde kullanmalısınız</li>
                    <li>Gerçek ve doğru bilgiler paylaşmalısınız</li>
                    <li>Başkalarının haklarına saygı göstermelisiniz</li>
                </ul>
                
                <h3>İlan Yayınlama</h3>
                <p>İlan yayınlarken, doğru ve eksiksiz bilgi vermeyi taahhüt edersiniz.</p>
            '''
        }
    return render_template('page.html', page=page_data)


@main_bp.route('/contact')
def contact():
    """Contact page"""
    page_data = get_page('iletisim')
    if not page_data:
        page_data = {
            'title': 'İletişim',
            'content': '''
                <h2>İletişim</h2>
                <p class="lead">Bizimle iletişime geçin, sorularınızı yanıtlamaktan memnuniyet duyarız.</p>
                
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <i class="fas fa-phone fa-2x text-primary mb-3"></i>
                            <h5>Telefon</h5>
                            <p class="text-muted">0 (850) 123 45 67</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <i class="fas fa-envelope fa-2x text-primary mb-3"></i>
                            <h5>E-posta</h5>
                            <p class="text-muted">info@360emlak.com</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <i class="fas fa-map-marker-alt fa-2x text-primary mb-3"></i>
                            <h5>Adres</h5>
                            <p class="text-muted">İstanbul, Türkiye</p>
                        </div>
                    </div>
                </div>
                
                <div class="mt-5">
                    <h3>Mesaj Gönderin</h3>
                    <form>
                        <div class="mb-3">
                            <label class="form-label">Ad Soyad</label>
                            <input type="text" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">E-posta</label>
                            <input type="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Mesajınız</label>
                            <textarea class="form-control" rows="5" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Gönder
                        </button>
                    </form>
                </div>
            '''
        }
    return render_template('page.html', page=page_data)

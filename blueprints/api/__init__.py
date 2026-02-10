"""
API Blueprint
AJAX endpoints for dynamic features
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from core.data_manager import get_data_manager

api_bp = Blueprint('api', __name__)


# Turkish Cities and Districts Data
TURKEY_CITIES_DISTRICTS = {
    "İstanbul": ["Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", 
                 "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", "Beyoğlu", "Büyükçekmece",
                 "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa",
                 "Güngören", "Kadıköy", "Kağıthane", "Kartal", "Küçükçekmece", "Maltepe", "Pendik",
                 "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli", "Sultangazi", "Şile", "Şişli",
                 "Tuzla", "Ümraniye", "Üsküdar", "Zeytinburnu"],
    
    "Ankara": ["Altındağ", "Ayaş", "Bala", "Beypazarı", "Çamlıdere", "Çankaya", "Çubuk", "Elmadağ",
               "Etimesgut", "Evren", "Gölbaşı", "Güdül", "Haymana", "Kahramankazan", "Kalecik",
               "Keçiören", "Kızılcahamam", "Mamak", "Nallıhan", "Polatlı", "Pursaklar", "Sincan",
               "Şereflikoçhisar", "Yenimahalle"],
    
    "İzmir": ["Aliağa", "Balçova", "Bayındır", "Bayraklı", "Bergama", "Beydağ", "Bornova", "Buca",
              "Çeşme", "Çiğli", "Dikili", "Foça", "Gaziemir", "Güzelbahçe", "Karabağlar", "Karaburun",
              "Karşıyaka", "Kemalpaşa", "Kınık", "Kiraz", "Konak", "Menderes", "Menemen", "Narlıdere",
              "Ödemiş", "Seferihisar", "Selçuk", "Tire", "Torbalı", "Urla"],
    
    "Antalya": ["Akseki", "Aksu", "Alanya", "Demre", "Döşemealtı", "Elmalı", "Finike", "Gazipaşa",
                "Gündoğmuş", "İbradı", "Kaş", "Kemer", "Kepez", "Konyaaltı", "Korkuteli", "Kumluca",
                "Manavgat", "Muratpaşa", "Serik"],
    
    "Bursa": ["Büyükorhan", "Gemlik", "Gürsu", "Harmancık", "İnegöl", "İznik", "Karacabey", "Keles",
              "Kestel", "Mudanya", "Mustafakemalpaşa", "Nilüfer", "Orhaneli", "Orhangazi", "Osmangazi",
              "Yenişehir", "Yıldırım"],
    
    "Adana": ["Aladağ", "Ceyhan", "Çukurova", "Feke", "İmamoğlu", "Karaisalı", "Karataş", "Kozan",
              "Pozantı", "Saimbeyli", "Sarıçam", "Seyhan", "Tufanbeyli", "Yumurtalık", "Yüreğir"]
}


@api_bp.route('/districts/<city>')
def get_districts(city):
    """Get districts for a given city"""
    districts = TURKEY_CITIES_DISTRICTS.get(city, [])
    return jsonify({
        'success': True,
        'city': city,
        'districts': sorted(districts)
    })


@api_bp.route('/cities')
def get_cities():
    """Get all cities"""
    cities = sorted(TURKEY_CITIES_DISTRICTS.keys())
    return jsonify({
        'success': True,
        'cities': cities
    })


@api_bp.route('/favorite/<property_id>', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    """Toggle favorite status for a property"""
    dm = get_data_manager()
    
    # Get user data
    user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
    
    if not user_data:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    # Initialize favorites list if not exists
    if 'favorites' not in user_data:
        user_data['favorites'] = []
    
    # Toggle favorite
    favorited = False
    if property_id in user_data['favorites']:
        user_data['favorites'].remove(property_id)
        favorited = False
    else:
        user_data['favorites'].append(property_id)
        favorited = True
    
    # Save changes
    dm.update_one('users', lambda u: u['id'] == current_user.id, user_data)
    
    return jsonify({
        'success': True,
        'favorited': favorited,
        'property_id': property_id
    })


@api_bp.route('/favorites')
@login_required
def get_favorites():
    """Get user's favorite properties"""
    dm = get_data_manager()
    
    # Get user data
    user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
    
    if not user_data:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    favorite_ids = user_data.get('favorites', [])
    
    # Get favorite properties
    favorite_properties = []
    for prop_id in favorite_ids:
        prop = dm.find_one('properties', lambda p: p['id'] == prop_id)
        if prop:
            favorite_properties.append(prop)
    
    return jsonify({
        'success': True,
        'favorites': favorite_properties
    })


@api_bp.route('/search')
def search_properties():
    """Search properties with filters (AJAX)"""
    dm = get_data_manager()
    
    # Get all active properties
    all_properties = dm.find_many('properties', lambda p: p.get('status') == 'active')
    
    # Apply filters
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
        'with_tour': request.args.get('with_tour') == 'true'
    }
    
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
    
    return jsonify({
        'success': True,
        'count': len(filtered_properties),
        'properties': filtered_properties
    })

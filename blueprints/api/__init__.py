"""
API Blueprint
AJAX endpoints for dynamic features
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from core.data_manager import get_data_manager
from core.mailer import send_new_message_notification, send_new_review_notification

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
        prop = dm.find_one('properties', lambda p, i=prop_id: p.get('id') == i)
        if prop:
            favorite_properties.append(prop)
    
    return jsonify({
        'success': True,
        'favorites': favorite_properties
    })


@api_bp.route('/contact/<property_id>', methods=['POST'])
@login_required
def send_contact_message(property_id):
    """Send a contact message to the property owner"""
    dm = get_data_manager()

    prop = dm.find_one('properties', lambda p: p.get('id') == property_id)
    if not prop:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404

    if prop.get('user_id') == current_user.id:
        return jsonify({'success': False, 'error': 'Kendi ilanınıza mesaj gönderemezsiniz'}), 400

    data = request.get_json() or {}
    message_text = (data.get('message') or '').strip()
    sender_name = (data.get('name') or current_user.name).strip()
    sender_phone = (data.get('phone') or '').strip()

    if not message_text:
        return jsonify({'success': False, 'error': 'Mesaj boş olamaz'}), 400
    if len(message_text) > 1000:
        return jsonify({'success': False, 'error': 'Mesaj çok uzun (max 1000 karakter)'}), 400

    import uuid
    from datetime import datetime
    msg = {
        'id': str(uuid.uuid4()),
        'property_id': property_id,
        'property_title': prop.get('title', ''),
        'owner_id': prop.get('user_id'),
        'sender_id': current_user.id,
        'sender_name': sender_name,
        'sender_email': current_user.email,
        'sender_phone': sender_phone,
        'message': message_text,
        'is_read': False,
        'created_at': datetime.now().isoformat(),
    }

    all_data = dm.read_all()
    if 'messages' not in all_data:
        all_data['messages'] = []
    all_data['messages'].append(msg)
    dm.write_all(all_data)

    # Email notification to property owner
    owner_data = dm.find_one('users', lambda u: u['id'] == prop.get('user_id'))
    if owner_data and owner_data.get('email'):
        send_new_message_notification(
            owner_email=owner_data['email'],
            owner_name=owner_data.get('name', ''),
            sender_name=sender_name,
            property_title=prop.get('title', ''),
            message_preview=message_text,
        )

    return jsonify({'success': True, 'message': 'Mesajınız iletildi'})


@api_bp.route('/messages')
@login_required
def get_messages():
    """Get messages received by the current user"""
    dm = get_data_manager()
    all_data = dm.read_all()
    msgs = [m for m in all_data.get('messages', []) if m.get('owner_id') == current_user.id]
    msgs.sort(key=lambda m: m.get('created_at', ''), reverse=True)
    return jsonify({'success': True, 'messages': msgs, 'unread': sum(1 for m in msgs if not m.get('is_read'))})


@api_bp.route('/messages/<msg_id>/read', methods=['POST'])
@login_required
def mark_message_read(msg_id):
    """Mark a message as read"""
    dm = get_data_manager()
    all_data = dm.read_all()
    for msg in all_data.get('messages', []):
        if msg.get('id') == msg_id and msg.get('owner_id') == current_user.id:
            msg['is_read'] = True
            dm.write_all(all_data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Mesaj bulunamadı'}), 404


@api_bp.route('/review/<property_id>', methods=['POST'])
@login_required
def submit_review(property_id):
    """Submit a star rating + comment for a property."""
    dm = get_data_manager()

    prop = dm.find_one('properties', lambda p: p.get('id') == property_id)
    if not prop:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404

    if prop.get('user_id') == current_user.id:
        return jsonify({'success': False, 'error': 'Kendi ilanınıza yorum yapamazsınız'}), 400

    data = request.get_json() or {}
    try:
        rating = int(data.get('rating', 0))
    except (TypeError, ValueError):
        rating = 0
    if rating < 1 or rating > 5:
        return jsonify({'success': False, 'error': 'Puan 1-5 arasında olmalıdır'}), 400

    comment = (data.get('comment') or '').strip()
    if len(comment) > 500:
        return jsonify({'success': False, 'error': 'Yorum 500 karakterden uzun olamaz'}), 400

    all_data = dm.read_all()
    reviews = all_data.setdefault('reviews', [])

    # One review per user per property
    for rev in reviews:
        if rev.get('property_id') == property_id and rev.get('user_id') == current_user.id:
            return jsonify({'success': False, 'error': 'Bu ilana zaten yorum yaptınız'}), 400

    import uuid
    from datetime import datetime
    review = {
        'id': str(uuid.uuid4()),
        'property_id': property_id,
        'user_id': current_user.id,
        'user_name': current_user.name,
        'rating': rating,
        'comment': comment,
        'created_at': datetime.now().isoformat(),
    }
    reviews.append(review)
    dm.write_all(all_data)

    # Email notification to property owner
    owner_data = dm.find_one('users', lambda u: u['id'] == prop.get('user_id'))
    if owner_data and owner_data.get('email'):
        send_new_review_notification(
            owner_email=owner_data['email'],
            owner_name=owner_data.get('name', ''),
            reviewer_name=current_user.name,
            property_title=prop.get('title', ''),
            rating=rating,
            comment=comment,
        )

    return jsonify({'success': True, 'review': review})


@api_bp.route('/review/<review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """Delete own review."""
    dm = get_data_manager()
    all_data = dm.read_all()
    reviews = all_data.get('reviews', [])
    for i, rev in enumerate(reviews):
        if rev.get('id') == review_id:
            if rev.get('user_id') != current_user.id and not current_user.is_admin():
                return jsonify({'success': False, 'error': 'Yetkisiz'}), 403
            reviews.pop(i)
            all_data['reviews'] = reviews
            dm.write_all(all_data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Yorum bulunamadı'}), 404


@api_bp.route('/saved-search', methods=['POST'])
@login_required
def save_search():
    """Save the current search criteria for the logged-in user."""
    data = request.get_json() or {}
    label = (data.get('label') or '').strip()[:80]
    params = data.get('params', {})
    if not params:
        return jsonify({'success': False, 'error': 'Arama parametresi boş'}), 400

    import uuid
    from datetime import datetime
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404

    searches = user_data.setdefault('saved_searches', [])
    if len(searches) >= 20:
        return jsonify({'success': False, 'error': 'En fazla 20 kayıtlı arama saklayabilirsiniz'}), 400

    entry = {
        'id': str(uuid.uuid4()),
        'label': label or 'Aramam',
        'params': params,
        'created_at': datetime.now().isoformat(),
    }
    searches.append(entry)
    dm.update_one('users', lambda u: u['id'] == current_user.id, user_data)
    return jsonify({'success': True, 'search': entry})


@api_bp.route('/saved-search/<search_id>', methods=['DELETE'])
@login_required
def delete_saved_search(search_id):
    """Remove a saved search."""
    dm = get_data_manager()
    user_data = dm.find_one('users', lambda u: u['id'] == current_user.id)
    if not user_data:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404

    searches = user_data.get('saved_searches', [])
    new_searches = [s for s in searches if s.get('id') != search_id]
    if len(new_searches) == len(searches):
        return jsonify({'success': False, 'error': 'Kayıt bulunamadı'}), 404

    user_data['saved_searches'] = new_searches
    dm.update_one('users', lambda u: u['id'] == current_user.id, user_data)
    return jsonify({'success': True})


@api_bp.route('/report/<property_id>', methods=['POST'])
@login_required
def report_property(property_id):
    """Report a property listing as inappropriate."""
    dm = get_data_manager()
    prop = dm.find_one('properties', lambda p: p.get('id') == property_id)
    if not prop:
        return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404

    if prop.get('user_id') == current_user.id:
        return jsonify({'success': False, 'error': 'Kendi ilanınızı şikayet edemezsiniz'}), 400

    data = request.get_json() or {}
    reason = (data.get('reason') or '').strip()
    VALID_REASONS = ['yaniltici', 'uygunsuz', 'kopya', 'yanlis_fiyat', 'diger']
    if reason not in VALID_REASONS:
        return jsonify({'success': False, 'error': 'Geçersiz şikayet nedeni'}), 400

    description = (data.get('description') or '').strip()[:300]

    all_data = dm.read_all()
    reports = all_data.setdefault('reports', [])

    # One report per user per property
    for rep in reports:
        if rep.get('property_id') == property_id and rep.get('reporter_id') == current_user.id:
            return jsonify({'success': False, 'error': 'Bu ilanı zaten şikayet ettiniz'}), 400

    import uuid
    from datetime import datetime
    report = {
        'id': str(uuid.uuid4()),
        'property_id': property_id,
        'property_title': prop.get('title', ''),
        'owner_id': prop.get('user_id'),
        'reporter_id': current_user.id,
        'reporter_name': current_user.name,
        'reason': reason,
        'description': description,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
    }
    reports.append(report)
    dm.write_all(all_data)
    return jsonify({'success': True, 'message': 'Şikayetiniz iletildi, inceleme yapılacak.'})


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
        
        if filters['min_price'] is not None and prop.get('price', 0) < filters['min_price']:
            continue

        if filters['max_price'] is not None and prop.get('price', 0) > filters['max_price']:
            continue

        if filters['min_area'] is not None and prop.get('area', 0) < filters['min_area']:
            continue

        if filters['max_area'] is not None and prop.get('area', 0) > filters['max_area']:
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

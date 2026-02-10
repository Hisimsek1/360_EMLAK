"""
Tour Blueprint Routes
360 Virtual Tour Management - Create, Edit, View Tours
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime

from blueprints.tour.forms import PropertyForm, SceneForm
from core.data_manager import get_data_manager
from core.utils import save_uploaded_file, process_360_image, create_thumbnail

tour_bp = Blueprint('tour', __name__, template_folder='../../templates/tour')


@tour_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new property with tour"""
    form = PropertyForm()
    dm = get_data_manager()
    
    # Populate dynamic choices
    data = dm.read_all()
    categories = data.get('categories', [])
    cities = data.get('cities', [])
    
    form.category.choices = [(cat['id'], cat['name']) for cat in categories]
    form.city.choices = [(city, city) for city in cities]
    
    if form.validate_on_submit():
        try:
            # Create property data
            property_id = str(uuid.uuid4())
            property_data = {
                'id': property_id,
                'user_id': current_user.id,
                'title': form.title.data,
                'description': form.description.data,
                'category': form.category.data,
                'listing_type': form.listing_type.data,
                'price': form.price.data,
                'city': form.city.data,
                'district': form.district.data,
                'address': form.address.data,
                'area': form.area.data,
                'rooms': form.rooms.data if form.rooms.data else '',
                'floor': form.floor.data if form.floor.data else '',
                'building_age': form.building_age.data if form.building_age.data else 0,
                'status': 'draft',  # draft, pending, active, inactive
                'views': 0,
                'images': [],  # Normal property photos
                'tour': {
                    'scenes': [],
                    'hotspots': []
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Handle normal photo uploads
            if form.images.data:
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', property_id)
                os.makedirs(upload_folder, exist_ok=True)
                
                for idx, photo in enumerate(form.images.data):
                    if photo and photo.filename:
                        # Generate unique filename
                        file_ext = photo.filename.rsplit('.', 1)[1].lower()
                        filename = f"photo_{idx + 1}_{uuid.uuid4().hex[:8]}.{file_ext}"
                        filepath = os.path.join(upload_folder, filename)
                        
                        # Save file
                        photo.save(filepath)
                        
                        # Process image (resize, optimize)
                        process_result = process_360_image(filepath, max_dimension=2048)
                        
                        if process_result['success']:
                            # Create thumbnail
                            thumb_filename = f"thumb_{filename}"
                            thumb_path = os.path.join(upload_folder, thumb_filename)
                            create_thumbnail(filepath, thumb_path, size=(400, 300))
                            
                            # Add to images array
                            property_data['images'].append({
                                'filename': filename,
                                'thumbnail': thumb_filename,
                                'order': idx
                            })
            
            # Save to database
            dm.insert_one('properties', property_data)
            
            flash('İlan oluşturuldu. Şimdi 360° tur ekleyebilirsiniz (opsiyonel).', 'success')
            return redirect(url_for('tour.editor', id=property_id))
        
        except Exception as e:
            flash(f'İlan oluşturulurken hata oluştu: {str(e)}', 'danger')
    
    return render_template('create.html', form=form)


@tour_bp.route('/editor/<id>')
@login_required
def editor(id):
    """360 Tour Editor"""
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p['id'] == id)
    
    if not property_data:
        flash('İlan bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check ownership
    if property_data['user_id'] != current_user.id and not current_user.is_admin():
        flash('Bu ilana erişim yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('editor.html', property=property_data)


@tour_bp.route('/api/upload-scene/<property_id>', methods=['POST'])
@login_required
def upload_scene(property_id):
    """Upload 360 scene image (API endpoint)"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Debug: Log request info
        print(f"Files received: {list(request.files.keys())}")
        print(f"Form data: {list(request.form.keys())}")
        print(f"Content-Type: {request.content_type}")
        
        # Check if file uploaded
        if 'image' not in request.files:
            return jsonify({
                'success': False, 
                'error': f'Dosya bulunamadı. Gönderilen alanlar: {list(request.files.keys())}'
            }), 400
        
        file = request.files['image']
        scene_name = request.form.get('name', 'Yeni Sahne')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Geçersiz dosya tipi'}), 400
        
        # Generate UUID filename
        scene_id = str(uuid.uuid4())
        filename = f"{scene_id}.jpg"
        
        # Create upload folder
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tours', property_id)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Process 360 image (EXIF fix, resize if needed)
        process_result = process_360_image(file_path, max_dimension=8192)
        
        if not process_result['success']:
            os.remove(file_path)
            return jsonify({
                'success': False,
                'error': f'Resim işleme hatası: {process_result.get("error", "Bilinmeyen hata")}'
            }), 400
        
        # Create thumbnail
        thumbnail_filename = f"{scene_id}_thumb.jpg"
        thumbnail_path = os.path.join(upload_folder, thumbnail_filename)
        create_thumbnail(file_path, thumbnail_path, size=(400, 300))
        
        # Create scene object
        scene = {
            'id': scene_id,
            'name': scene_name,
            'filename': filename,
            'thumbnail': thumbnail_filename,
            'width': process_result['width'],
            'height': process_result['height'],
            'size': process_result['size_bytes'],
            'hotspots': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Update property tour data
        if 'tour' not in property_data:
            property_data['tour'] = {'scenes': [], 'hotspots': []}
        
        property_data['tour']['scenes'].append(scene)
        property_data['updated_at'] = datetime.now().isoformat()
        
        # Save to database
        dm.update_one(
            'properties',
            lambda p: p['id'] == property_id,
            property_data
        )
        
        return jsonify({
            'success': True,
            'scene': scene,
            'message': 'Sahne başarıyla yüklendi'
        })
    
    except Exception as e:
        current_app.logger.error(f"Scene upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tour_bp.route('/api/delete-scene/<property_id>/<scene_id>', methods=['DELETE'])
@login_required
def delete_scene(property_id, scene_id):
    """Delete 360 scene"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Find and remove scene
        scenes = property_data.get('tour', {}).get('scenes', [])
        scene_to_delete = None
        
        for i, scene in enumerate(scenes):
            if scene['id'] == scene_id:
                scene_to_delete = scenes.pop(i)
                break
        
        if not scene_to_delete:
            return jsonify({'success': False, 'error': 'Sahne bulunamadı'}), 404
        
        # Delete files
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tours', property_id)
        
        try:
            file_path = os.path.join(upload_folder, scene_to_delete['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            thumb_path = os.path.join(upload_folder, scene_to_delete['thumbnail'])
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting files: {str(e)}")
        
        # Update database
        property_data['updated_at'] = datetime.now().isoformat()
        dm.update_one(
            'properties',
            lambda p: p['id'] == property_id,
            property_data
        )
        
        return jsonify({'success': True, 'message': 'Sahne silindi'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tour_bp.route('/api/save-hotspots/<property_id>', methods=['POST'])
@login_required
def save_hotspots(property_id):
    """Save hotspot data for property tour"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Get hotspot data from request
        hotspot_data = request.get_json()
        
        if not hotspot_data:
            return jsonify({'success': False, 'error': 'Hotspot verisi bulunamadı'}), 400
        
        # Update tour data
        if 'tour' not in property_data:
            property_data['tour'] = {'scenes': [], 'hotspots': []}
        
        property_data['tour']['hotspots'] = hotspot_data
        property_data['updated_at'] = datetime.now().isoformat()
        
        # Save to database
        dm.update_one(
            'properties',
            lambda p: p['id'] == property_id,
            property_data
        )
        
        return jsonify({'success': True, 'message': 'Hotspotlar kaydedildi'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tour_bp.route('/api/publish/<property_id>', methods=['POST'])
@login_required
def publish(property_id):
    """Publish property tour"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Validate tour has scenes
        scenes = property_data.get('tour', {}).get('scenes', [])
        if len(scenes) == 0:
            return jsonify({
                'success': False,
                'error': 'Yayınlamak için en az 1 sahne eklemelisiniz'
            }), 400
        
        # Update status
        property_data['status'] = 'active'
        property_data['updated_at'] = datetime.now().isoformat()
        property_data['published_at'] = datetime.now().isoformat()
        
        # Save to database
        dm.update_one(
            'properties',
            lambda p: p['id'] == property_id,
            property_data
        )
        
        return jsonify({
            'success': True,
            'message': 'İlan yayınlandı',
            'redirect': url_for('tour.view', id=property_id)
        })
    
    except Exception as e:
        import traceback
        print(f"Publish error: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@tour_bp.route('/view/<id>')
def view(id):
    """View published tour"""
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p['id'] == id)
    
    if not property_data:
        flash('İlan bulunamadı.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if published or owner
    if property_data['status'] != 'active':
        if not current_user.is_authenticated or \
           (property_data['user_id'] != current_user.id and not current_user.is_admin()):
            flash('Bu ilan henüz yayınlanmamış.', 'warning')
            return redirect(url_for('main.index'))
    
    # Get property owner information
    owner = None
    if property_data.get('user_id'):
        owner_data = dm.find_one('users', lambda u: u['id'] == property_data['user_id'])
        if owner_data:
            owner = {
                'id': owner_data.get('id'),
                'name': owner_data.get('name'),
                'email': owner_data.get('email'),
                'phone': owner_data.get('phone', ''),
                'photo_url': owner_data.get('photo_url', ''),
                'profession': owner_data.get('profession', ''),
                'city': owner_data.get('city', '')
            }
    
    # Increment view count
    if not current_user.is_authenticated or property_data['user_id'] != current_user.id:
        property_data['views'] = property_data.get('views', 0) + 1
        dm.update_one(
            'properties',
            lambda p: p['id'] == id,
            property_data
        )
    
    return render_template('view.html', property=property_data, owner=owner)


@tour_bp.route('/edit/<property_id>', methods=['GET', 'POST'])
@login_required
def edit(property_id):
    """Edit existing property"""
    dm = get_data_manager()
    property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
    
    if not property_data:
        flash('İlan bulunamadı.', 'danger')
        return redirect(url_for('dashboard.properties'))
    
    # Check ownership
    if property_data['user_id'] != current_user.id and not current_user.is_admin():
        flash('Bu ilana erişim yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard.properties'))
    
    form = PropertyForm()
    
    # Populate dynamic choices
    data = dm.read_all()
    categories = data.get('categories', [])
    cities = data.get('cities', [])
    
    form.category.choices = [(cat['id'], cat['name']) for cat in categories]
    form.city.choices = [(city, city) for city in cities]
    
    if form.validate_on_submit():
        try:
            # Update property data
            property_data.update({
                'title': form.title.data,
                'description': form.description.data,
                'category': form.category.data,
                'listing_type': form.listing_type.data,
                'price': form.price.data,
                'city': form.city.data,
                'district': form.district.data,
                'address': form.address.data,
                'area': form.area.data,
                'rooms': form.rooms.data if form.rooms.data else '',
                'floor': form.floor.data if form.floor.data else '',
                'building_age': form.building_age.data if form.building_age.data else 0,
                'updated_at': datetime.now().isoformat()
            })
            
            # Save to database
            dm.update('properties', lambda p: p['id'] == property_id, property_data)
            
            flash('İlan başarıyla güncellendi.', 'success')
            return redirect(url_for('tour.editor', id=property_id))
        
        except Exception as e:
            flash(f'İlan güncellenirken hata oluştu: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        # Pre-fill form with existing data
        form.title.data = property_data.get('title')
        form.description.data = property_data.get('description')
        form.category.data = property_data.get('category')
        form.listing_type.data = property_data.get('listing_type')
        form.price.data = property_data.get('price')
        form.city.data = property_data.get('city')
        form.district.data = property_data.get('district')
        form.address.data = property_data.get('address')
        form.area.data = property_data.get('area')
        form.rooms.data = property_data.get('rooms')
        form.floor.data = property_data.get('floor')
        form.building_age.data = property_data.get('building_age')
    
    return render_template('edit.html', form=form, property=property_data)


@tour_bp.route('/delete/<property_id>', methods=['POST'])
@login_required
def delete(property_id):
    """Delete property and all associated files"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Delete uploaded files
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tours', property_id)
        if os.path.exists(upload_dir):
            import shutil
            try:
                shutil.rmtree(upload_dir)
            except Exception as e:
                current_app.logger.error(f'Error deleting files: {e}')
        
        # Delete from database
        dm.delete_one('properties', lambda p: p['id'] == property_id)
        
        return jsonify({
            'success': True,
            'message': 'İlan ve tüm dosyaları başarıyla silindi'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tour_bp.route('/unpublish/<property_id>', methods=['POST'])
@login_required
def unpublish(property_id):
    """Unpublish property (set to draft)"""
    try:
        dm = get_data_manager()
        property_data = dm.find_one('properties', lambda p: p['id'] == property_id)
        
        if not property_data:
            return jsonify({'success': False, 'error': 'İlan bulunamadı'}), 404
        
        # Check ownership
        if property_data['user_id'] != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Update status
        property_data['status'] = 'draft'
        property_data['updated_at'] = datetime.now().isoformat()
        
        # Save to database
        dm.update('properties', lambda p: p['id'] == property_id, property_data)
        
        return jsonify({
            'success': True,
            'message': 'İlan yayından kaldırıldı'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


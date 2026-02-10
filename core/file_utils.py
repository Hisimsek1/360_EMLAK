"""
File Utils for 360EV
Handles missing files with graceful fallbacks
"""
import os
from flask import current_app, url_for


def get_safe_image_url(filepath, fallback_type="property"):
    """
    Returns a safe image URL with fallback for missing files
    
    Args:
        filepath: Relative path to the image 
        fallback_type: Type of fallback image (property, avatar, 360)
    """
    if not filepath:
        return get_fallback_image(fallback_type)
    
    # Check if file exists
    full_path = os.path.join(current_app.static_folder, filepath.replace('/static/', ''))
    
    if os.path.exists(full_path):
        return url_for('static', filename=filepath.replace('/static/', ''))
    else:
        return get_fallback_image(fallback_type)


def get_fallback_image(image_type):
    """Get appropriate fallback image based on type"""
    fallbacks = {
        'property': '/static/images/placeholders/property-placeholder.jpg',
        'avatar': '/static/images/placeholders/avatar-placeholder.jpg', 
        '360': '/static/images/placeholders/360-placeholder.jpg',
        'thumbnail': '/static/images/placeholders/thumb-placeholder.jpg'
    }
    
    return fallbacks.get(image_type, '/static/images/placeholders/default-placeholder.jpg')


def ensure_placeholder_images():
    """Ensure placeholder images exist in static folder"""
    placeholders_dir = os.path.join(current_app.static_folder, 'images', 'placeholders')
    
    if not os.path.exists(placeholders_dir):
        os.makedirs(placeholders_dir)
    
    # You can add logic here to download/create actual placeholder images
    # Or use CSS-generated placeholders
    
    return True
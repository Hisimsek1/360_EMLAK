"""
Property Blueprint Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for
from core.data_manager import get_data_manager

property_bp = Blueprint('property', __name__, template_folder='../../templates/property')


@property_bp.route('/')
def index():
    """Property listings page"""
    dm = get_data_manager()
    
    # Get all active properties
    all_properties = dm.find_many('properties', lambda p: p.get('status') == 'active')
    
    # Sort by date (newest first)
    all_properties.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    
    return render_template('property/list.html', properties=all_properties)


@property_bp.route('/<int:property_id>')
def detail(property_id):
    """Property detail page - To be implemented"""
    return f"Property {property_id} detail - Coming soon"

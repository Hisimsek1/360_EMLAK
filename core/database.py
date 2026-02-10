"""
JSON Database Operations
Handles all read/write operations to data.json
"""
import json
import os
from threading import Lock
from typing import Optional, List, Dict, Any
from datetime import datetime


class JSONDatabase:
    """Thread-safe JSON database manager"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.lock = Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create data file if it doesn't exist"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._write_data({
                "users": [],
                "properties": [],
                "settings": {},
                "pages": {},
                "categories": [],
                "cities": []
            })
    
    def _read_data(self) -> Dict[str, Any]:
        """Read data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "users": [],
                "properties": [],
                "settings": {},
                "pages": {},
                "categories": [],
                "cities": []
            }
    
    def _write_data(self, data: Dict[str, Any]):
        """Write data to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def read(self) -> Dict[str, Any]:
        """Thread-safe read"""
        with self.lock:
            return self._read_data()
    
    def write(self, data: Dict[str, Any]):
        """Thread-safe write"""
        with self.lock:
            self._write_data(data)
    
    def get_collection(self, collection_name: str) -> List[Dict]:
        """Get a collection from database"""
        data = self.read()
        return data.get(collection_name, [])
    
    def update_collection(self, collection_name: str, collection_data: List[Dict]):
        """Update a collection in database"""
        data = self.read()
        data[collection_name] = collection_data
        self.write(data)


# Global database instance
_db_instance: Optional[JSONDatabase] = None


def init_database(data_file: str):
    """Initialize the database"""
    global _db_instance
    _db_instance = JSONDatabase(data_file)


def get_database() -> JSONDatabase:
    """Get database instance"""
    if _db_instance is None:
        from flask import current_app
        init_database(current_app.config['DATA_FILE'])
    return _db_instance


# User operations
def get_users() -> List[Dict]:
    """Get all users"""
    return get_database().get_collection('users')


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    users = get_users()
    for user in users:
        if user.get('id') == user_id:
            return user
    return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    users = get_users()
    for user in users:
        if user.get('email') == email:
            return user
    return None


def create_user(user_data: Dict) -> Dict:
    """Create a new user"""
    users = get_users()
    user_data['created_at'] = datetime.now().isoformat()
    users.append(user_data)
    get_database().update_collection('users', users)
    return user_data


def update_user(user_id: str, user_data: Dict) -> bool:
    """Update user data"""
    users = get_users()
    for i, user in enumerate(users):
        if user.get('id') == user_id:
            user_data['updated_at'] = datetime.now().isoformat()
            users[i] = {**user, **user_data}
            get_database().update_collection('users', users)
            return True
    return False


def delete_user(user_id: str) -> bool:
    """Delete a user"""
    users = get_users()
    users = [u for u in users if u.get('id') != user_id]
    get_database().update_collection('users', users)
    return True


# Property operations
def get_properties(filters: Optional[Dict] = None) -> List[Dict]:
    """Get properties with optional filters"""
    properties = get_database().get_collection('properties')
    
    if not filters:
        return properties
    
    # Apply filters
    filtered = properties
    
    if 'user_id' in filters:
        filtered = [p for p in filtered if p.get('user_id') == filters['user_id']]
    
    if 'category' in filters:
        filtered = [p for p in filtered if p.get('category') == filters['category']]
    
    if 'city' in filters:
        filtered = [p for p in filtered if p.get('city') == filters['city']]
    
    if 'listing_type' in filters:
        filtered = [p for p in filtered if p.get('listing_type') == filters['listing_type']]
    
    if 'status' in filters:
        filtered = [p for p in filtered if p.get('status') == filters['status']]
    
    return filtered


def get_property_by_id(property_id: str) -> Optional[Dict]:
    """Get property by ID"""
    properties = get_properties()
    for prop in properties:
        if prop.get('id') == property_id:
            return prop
    return None


def create_property(property_data: Dict) -> Dict:
    """Create a new property"""
    properties = get_properties()
    property_data['created_at'] = datetime.now().isoformat()
    property_data['updated_at'] = datetime.now().isoformat()
    properties.append(property_data)
    get_database().update_collection('properties', properties)
    return property_data


def update_property(property_id: str, property_data: Dict) -> bool:
    """Update property data"""
    properties = get_properties()
    for i, prop in enumerate(properties):
        if prop.get('id') == property_id:
            property_data['updated_at'] = datetime.now().isoformat()
            properties[i] = {**prop, **property_data}
            get_database().update_collection('properties', properties)
            return True
    return False


def delete_property(property_id: str) -> bool:
    """Delete a property"""
    properties = get_properties()
    properties = [p for p in properties if p.get('id') != property_id]
    get_database().update_collection('properties', properties)
    return True


# Page operations
def get_pages() -> Dict[str, Dict]:
    """Get all pages"""
    data = get_database().read()
    return data.get('pages', {})


def get_page(slug: str) -> Optional[Dict]:
    """Get page by slug"""
    pages = get_pages()
    return pages.get(slug)


def update_page(slug: str, page_data: Dict) -> bool:
    """Update page data"""
    data = get_database().read()
    if 'pages' not in data:
        data['pages'] = {}
    
    page_data['updated_at'] = datetime.now().isoformat()
    data['pages'][slug] = page_data
    get_database().write(data)
    return True


# Settings operations
def get_settings() -> Dict:
    """Get site settings"""
    data = get_database().read()
    return data.get('settings', {})


def update_settings(settings_data: Dict) -> bool:
    """Update site settings"""
    data = get_database().read()
    data['settings'] = {**data.get('settings', {}), **settings_data}
    get_database().write(data)
    return True


# Category operations
def get_categories() -> List[Dict]:
    """Get all categories"""
    return get_database().get_collection('categories')


# City operations
def get_cities() -> List[str]:
    """Get all cities"""
    return get_database().get_collection('cities')

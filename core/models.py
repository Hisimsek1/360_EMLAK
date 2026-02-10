"""
User Model for Flask-Login
Represents a user in the system with password hashing support
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import datetime
import uuid


class User(UserMixin):
    """User model for authentication with pbkdf2:sha256 password hashing"""
    
    def __init__(self, user_data: dict):
        """
        Initialize user from dictionary
        
        Args:
            user_data (dict): User data from database
        """
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.name = user_data.get('name')
        self.phone = user_data.get('phone', '')
        self.role = user_data.get('role', 'user')  # user, admin, super_admin
        self.password_hash = user_data.get('password_hash', '')
        self._is_active = user_data.get('is_active', True)
        self.email_verified = user_data.get('email_verified', False)
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
        self.last_login = user_data.get('last_login')
        # Profile fields
        self.bio = user_data.get('bio', '')
        self.photo_url = user_data.get('photo_url', '')
        self.city = user_data.get('city', '')
        self.profession = user_data.get('profession', '')
    
    def get_id(self):
        """Return user ID as string (required by Flask-Login)"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Return True if user account is active"""
        return self._is_active
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    @property
    def is_anonymous(self):
        """Return False for logged-in users"""
        return False
    
    def set_password(self, password: str):
        """
        Hash and set password using pbkdf2:sha256
        
        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password to check
        
        Returns:
            bool: True if password matches
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role in ['admin', 'super_admin']
    
    def is_agent(self) -> bool:
        """Check if user has agent role"""
        return self.role == 'agent'
    
    def is_super_admin(self) -> bool:
        """Check if user has super_admin role"""
        return self.role == 'super_admin'
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
    
    def to_dict(self, include_password: bool = False) -> dict:
        """
        Convert user to dictionary
        
        Args:
            include_password: Include password hash in output
        
        Returns:
            dict: User data
        """
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data
    
    @staticmethod
    def create_new_user(email: str, name: str, password: str, phone: str = '', 
                       role: str = 'user') -> dict:
        """
        Create new user dictionary with hashed password
        
        Args:
            email: User email
            name: User name
            password: Plain text password
            phone: User phone (optional)
            role: User role (user, admin, super_admin)
        
        Returns:
            dict: User data ready for database
        """
        # Auto-assign super_admin role to specific email
        if email == 'mserdarsokmen@gmail.com':
            role = 'super_admin'
        
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'name': name,
            'phone': phone,
            'role': role,
            'password_hash': generate_password_hash(password, method='pbkdf2:sha256'),
            'is_active': True,
            'email_verified': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        return user_data
    
    def __repr__(self):
        return f'<User {self.email}>'

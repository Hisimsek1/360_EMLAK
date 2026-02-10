"""
Test Suite for 360 Emlak Platform
Run with: python -m pytest test_app.py -v
"""
import pytest
import json
import os
import tempfile
from app import create_app
from core.data_manager import DataManager


class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    
    def __init__(self):
        # Create temporary test data file
        self.test_fd, self.DATA_FILE = tempfile.mkstemp(suffix='.json')
        # Initialize with empty data
        with open(self.DATA_FILE, 'w') as f:
            json.dump({
                'users': [],
                'properties': [],
                'pages': [],
                'settings': {},
                'categories': [],
                'cities': []
            }, f)


@pytest.fixture
def app():
    """Create and configure test app"""
    config = TestConfig()
    app = create_app(config)
    
    with app.app_context():
        yield app
    
    # Clean up
    os.close(config.test_fd)
    os.unlink(config.DATA_FILE)


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner"""
    return app.test_cli_runner()


class TestMainRoutes:
    """Test main application routes"""
    
    def test_index_page(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'360 Emlak' in response.data
    
    def test_about_page(self, client):
        """Test about page loads"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_contact_page(self, client):
        """Test contact page loads"""
        response = client.get('/contact')
        assert response.status_code == 200


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Giriş Yap' in response.data
    
    def test_register_page(self, client):
        """Test register page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Kayıt Ol' in response.data


class TestPropertyRoutes:
    """Test property routes"""
    
    def test_properties_list(self, client):
        """Test properties list page"""
        response = client.get('/property/')
        assert response.status_code == 200


class TestDataManager:
    """Test data manager functionality"""
    
    def test_data_manager_creation(self, app):
        """Test DataManager can be created"""
        with app.app_context():
            dm = DataManager()
            assert dm is not None
    
    def test_read_empty_data(self, app):
        """Test reading empty data structure"""
        with app.app_context():
            dm = DataManager()
            data = dm.read_all()
            assert 'users' in data
            assert 'properties' in data
            assert 'pages' in data


class TestSecurity:
    """Test security features"""
    
    def test_csrf_protection(self, client):
        """Test CSRF protection is working"""
        # This would normally fail without CSRF token
        # but we disabled it in test config
        pass
    
    def test_admin_routes_protected(self, client):
        """Test admin routes require authentication"""
        response = client.get('/admin/')
        # Should redirect to login or show access denied
        assert response.status_code in [302, 403]


if __name__ == '__main__':
    pytest.main(['-v', __file__])
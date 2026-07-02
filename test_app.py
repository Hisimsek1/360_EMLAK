# -*- coding: utf-8 -*-
"""
Test Suite for 360 Emlak Platform
Run with: python -m pytest test_app.py -v
"""
import os
import json
import tempfile

import pytest

from app import create_app
from core.data_manager import DataManager, init_data_manager
from config import TestingConfig


@pytest.fixture
def app():
    """Create and configure a test app with an isolated temp data file."""
    fd, data_file = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump({
            'users': [], 'properties': [], 'messages': [],
            'settings': {}, 'pages': {}, 'categories': [], 'cities': []
        }, f)

    # Point the app (and the global data manager) at the temp file.
    TestingConfig.DATA_FILE = data_file
    app = create_app('testing')
    init_data_manager(data_file, backup_enabled=False)

    with app.app_context():
        yield app

    os.unlink(data_file)


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


class TestMainRoutes:
    """Test main application routes"""

    def test_index_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert '360 Emlak' in response.get_data(as_text=True)

    def test_about_page(self, client):
        assert client.get('/about').status_code == 200

    def test_contact_page(self, client):
        assert client.get('/contact').status_code == 200


class TestAuthRoutes:
    """Test authentication routes"""

    def test_login_page(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert 'Giriş' in response.get_data(as_text=True)

    def test_register_page(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert 'Kayıt' in response.get_data(as_text=True)


class TestPropertyRoutes:
    """Test property routes"""

    def test_properties_list(self, client):
        assert client.get('/property/').status_code == 200


class TestDataManager:
    """Test data manager functionality"""

    def test_data_manager_creation(self):
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            dm = DataManager(path, backup_enabled=False)
            assert dm is not None
            data = dm.read_all()
            assert 'users' in data
            assert 'properties' in data
        finally:
            os.unlink(path)

    def test_insert_and_find(self):
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            dm = DataManager(path, backup_enabled=False)
            dm.insert_one('users', {'id': 'u1', 'email': 'a@b.com'})
            found = dm.find_one('users', lambda u: u['id'] == 'u1')
            assert found is not None
            assert found['email'] == 'a@b.com'
        finally:
            os.unlink(path)


class TestSecurity:
    """Test security features"""

    def test_admin_routes_protected(self, client):
        """Admin routes must require authentication (redirect to login)."""
        response = client.get('/admin/')
        assert response.status_code in (302, 403)

    def test_dashboard_protected(self, client):
        response = client.get('/dashboard/')
        assert response.status_code in (302, 403)


if __name__ == '__main__':
    pytest.main(['-v', __file__])

import pytest
import os
import sys

# Añadir el directorio app al path para importar app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    """Test que verifica que la página de login carga correctamente"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    """Test que verifica que la página de registro carga correctamente"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Registro' in response.data

def test_home_page_redirect(client):
    """Test que verifica que home redirige a login cuando no hay sesión"""
    response = client.get('/')
    assert response.status_code == 302  # Redirige a login
    assert '/login' in response.location

def test_valid_email():
    """Test de la función valid_email"""
    from app import valid_email
    assert valid_email('test@example.com') is not None
    assert valid_email('invalid-email') is None

def test_health_check(client):
    """Test básico de salud de la aplicación"""
    response = client.get('/login')
    assert response.status_code == 200

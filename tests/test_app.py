import pytest
from backend import create_app
from backend.extensions import db

@pytest.fixture()
def app():
    app=create_app({"TESTING":True,"WTF_CSRF_ENABLED":False,"SQLALCHEMY_DATABASE_URI":"sqlite://","SECRET_KEY":"test-key"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def test_home(client):
    r=client.get("/")
    assert r.status_code==200
    assert b"Santa Rita de Casia" in r.data

def test_three_login_pages(client):
    for p in ("/auth/padres","/auth/personal","/auth/direccion"):
        assert client.get(p).status_code==200

def test_public_tracking_page(client):
    assert client.get("/tramites/consultar").status_code==200

def test_parent_panel_requires_login(client):
    assert client.get("/padres/").status_code==302

def test_staff_inbox_requires_login(client):
    assert client.get("/tramites/").status_code==302

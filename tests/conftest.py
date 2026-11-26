import pytest

from app import create_app
from app.extensions import db
from app.seed import cargar_datos


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with application.app_context():
        db.create_all()
        cargar_datos()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

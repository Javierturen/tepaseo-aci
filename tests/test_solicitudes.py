from datetime import date, timedelta

import pytest

from app.extensions import db
from app.models import Cliente, Comuna, Servicio, SolicitudPaseo


@pytest.fixture
def datos_solicitud(app):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )

        servicio = db.session.scalar(
            db.select(Servicio).filter_by(nombre="Paseo básico")
        )

        return {
            "nombre": "Cliente Demo",
            "correo": "cliente@example.com",
            "telefono": "+56912345678",
            "nombre_mascota": "Max",
            "raza": "Labrador",
            "tamano": "grande",
            "comuna": comuna.id,
            "servicio": servicio.id,
            "fecha": (
                date.today() + timedelta(days=2)
            ).isoformat(),
            "horario": "10:00",
            "observaciones": "Perro tranquilo.",
            "acepta_datos": "y",
        }


def cantidad_solicitudes(app):
    with app.app_context():
        return len(
            db.session.scalars(
                db.select(SolicitudPaseo)
            ).all()
        )


def test_formulario_solicitud(client):
    response = client.get("/solicitar-paseo")

    assert response.status_code == 200
    assert "Solicita un paseo" in response.get_data(
        as_text=True
    )


def test_solicitud_valida(app, client, datos_solicitud):
    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Solicitud recibida correctamente" in (
        response.get_data(as_text=True)
    )

    with app.app_context():
        solicitud = db.session.scalar(
            db.select(SolicitudPaseo)
        )

        assert solicitud is not None
        assert solicitud.estado == "pendiente"
        assert solicitud.nombre_mascota == "Max"
        assert solicitud.cliente.nombre == "Cliente Demo"
        assert solicitud.comuna.nombre == "Providencia"
        assert solicitud.servicio.nombre == "Paseo básico"

        clientes = db.session.scalars(
            db.select(Cliente)
        ).all()

        assert len(clientes) == 1


def test_nombre_vacio(app, client, datos_solicitud):
    datos_solicitud["nombre"] = ""

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_correo_invalido(app, client, datos_solicitud):
    datos_solicitud["correo"] = "correo-invalido"

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_telefono_invalido(app, client, datos_solicitud):
    datos_solicitud["telefono"] = "123"

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_fecha_pasada(app, client, datos_solicitud):
    datos_solicitud["fecha"] = (
        date.today() - timedelta(days=1)
    ).isoformat()

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert "No puedes seleccionar una fecha pasada" in (
        response.get_data(as_text=True)
    )

    assert cantidad_solicitudes(app) == 0


def test_comuna_no_habilitada(app, client, datos_solicitud):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Maipú")
        )

        datos_solicitud["comuna"] = comuna.id

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_servicio_no_activo(app, client, datos_solicitud):
    with app.app_context():
        servicio = db.session.get(
            Servicio, datos_solicitud["servicio"]
        )

        servicio.activo = False
        db.session.commit()

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_sin_autorizacion(app, client, datos_solicitud):
    datos_solicitud.pop("acepta_datos")

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_tamano_invalido(app, client, datos_solicitud):
    datos_solicitud["tamano"] = "inexistente"

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 200
    assert cantidad_solicitudes(app) == 0


def test_proteccion_csrf(app, client, datos_solicitud):
    app.config["WTF_CSRF_ENABLED"] = True

    response = client.post(
        "/solicitar-paseo",
        data=datos_solicitud,
    )

    assert response.status_code == 400
    assert cantidad_solicitudes(app) == 0

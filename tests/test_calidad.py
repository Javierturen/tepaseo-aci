from datetime import date, timedelta

import pytest

from app import cargar_usuario
from app.extensions import db
from app.models import (
    Administrador,
    Comuna,
    Postulacion,
    Servicio,
    SolicitudPaseo,
)


@pytest.mark.parametrize(
    "identificador",
    ["identificador-invalido", None],
)
def test_identificador_admin_invalido(app, identificador):
    with app.app_context():
        assert cargar_usuario(identificador) is None


def test_admin_autenticado_no_repite_login(app, client):
    contrasena = "Clave-exclusiva-de-pruebas-2026"

    with app.app_context():
        admin = Administrador(usuario="admin-prueba")
        admin.establecer_contrasena(contrasena)

        db.session.add(admin)
        db.session.commit()

    response = client.post(
        "/admin/login",
        data={
            "usuario": "admin-prueba",
            "contrasena": contrasena,
        },
    )

    assert response.status_code == 302

    response = client.get("/admin/login")

    assert response.status_code == 302
    assert response.location.endswith("/admin/")


def test_normalizacion_solicitud(app, client):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )

        servicio = db.session.scalar(
            db.select(Servicio).filter_by(nombre="Paseo básico")
        )

        comuna_id = comuna.id
        servicio_id = servicio.id

    fecha = date.today() + timedelta(days=2)

    response = client.post(
        "/solicitar-paseo",
        data={
            "nombre": "  Cliente Demo  ",
            "correo": "  cliente@example.com  ",
            "telefono": "+56 9 1234 5678",
            "nombre_mascota": "  Max  ",
            "raza": "  Labrador  ",
            "tamano": "grande",
            "comuna": comuna_id,
            "servicio": servicio_id,
            "fecha": fecha.isoformat(),
            "horario": "10:00",
            "observaciones": "  Perro tranquilo.  ",
            "acepta_datos": "y",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        solicitud = db.session.scalar(
            db.select(SolicitudPaseo)
        )

        assert solicitud is not None
        assert solicitud.cliente.nombre == "Cliente Demo"
        assert solicitud.cliente.correo == "cliente@example.com"
        assert solicitud.cliente.telefono == "+56912345678"
        assert solicitud.nombre_mascota == "Max"
        assert solicitud.raza == "Labrador"
        assert solicitud.observaciones == "Perro tranquilo."


def test_normalizacion_postulacion(app, client):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )

        comuna_id = comuna.id

    response = client.post(
        "/trabaja-con-nosotros",
        data={
            "nombre": "\t Paseador Demo  ",
            "correo": "  paseador@example.com  ",
            "telefono": "+56 9 8765 4321",
            "comuna": comuna_id,
            "experiencia": "  Experiencia con perros.  ",
            "disponibilidad": "  Lunes a viernes.  ",
            "acepta_datos": "y",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        postulacion = db.session.scalar(
            db.select(Postulacion)
        )

        assert postulacion is not None
        assert postulacion.nombre == "Paseador Demo"
        assert postulacion.correo == "paseador@example.com"
        assert postulacion.telefono == "+56987654321"
        assert postulacion.experiencia == "Experiencia con perros."
        assert postulacion.disponibilidad == "Lunes a viernes."


@pytest.mark.parametrize(
    "archivo",
    [
        "logo.svg",
        "hero.svg",
        "styles.css",
        "admin.css",
    ],
)
def test_archivos_estaticos(client, archivo):
    response = client.get(f"/static/{archivo}")

    assert response.status_code == 200
    assert len(response.data) > 0


def test_portada_solo_servicios_activos(app, client):
    with app.app_context():
        servicio = Servicio(
            nombre="Servicio oculto de prueba",
            descripcion="Servicio no disponible.",
            duracion=30,
            precio=5000,
            activo=False,
        )

        db.session.add(servicio)
        db.session.commit()

    response = client.get("/")

    contenido = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Paseo básico" in contenido
    assert "Servicio oculto de prueba" not in contenido

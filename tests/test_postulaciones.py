import pytest

from app.extensions import db
from app.models import Comuna, Postulacion


@pytest.fixture
def datos_postulacion(app):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )

        return {
            "nombre": "Paseador Demo",
            "correo": "paseador@example.com",
            "telefono": "+56987654321",
            "comuna": comuna.id,
            "experiencia": "Experiencia cuidando perros.",
            "disponibilidad": "Lunes a viernes.",
            "acepta_datos": "y",
        }


def cantidad_postulaciones(app):
    with app.app_context():
        return len(
            db.session.scalars(
                db.select(Postulacion)
            ).all()
        )


def test_formulario_postulacion(client):
    response = client.get("/trabaja-con-nosotros")

    assert response.status_code == 200
    assert "Formulario de postulación" in (
        response.get_data(as_text=True)
    )


@pytest.mark.parametrize(
    "nombre_comuna",
    ["Providencia", "Maipú"],
)
def test_postulacion_valida(
    app, client, datos_postulacion, nombre_comuna
):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre=nombre_comuna)
        )
        datos_postulacion["comuna"] = comuna.id

    response = client.post(
        "/trabaja-con-nosotros",
        data=datos_postulacion,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Postulación recibida correctamente" in (
        response.get_data(as_text=True)
    )

    with app.app_context():
        postulacion = db.session.scalar(
            db.select(Postulacion)
        )

        assert postulacion is not None
        assert postulacion.nombre == "Paseador Demo"
        assert postulacion.estado == "recibida"
        assert postulacion.comuna.nombre == nombre_comuna


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nombre", ""),
        ("correo", "correo-invalido"),
        ("telefono", "123"),
        ("experiencia", ""),
        ("disponibilidad", ""),
    ],
)
def test_postulacion_datos_invalidos(
    app, client, datos_postulacion, campo, valor
):
    datos_postulacion[campo] = valor

    response = client.post(
        "/trabaja-con-nosotros",
        data=datos_postulacion,
    )

    assert response.status_code == 200
    assert cantidad_postulaciones(app) == 0


def test_postulacion_comuna_invalida(
    app, client, datos_postulacion
):
    datos_postulacion["comuna"] = 9999

    response = client.post(
        "/trabaja-con-nosotros",
        data=datos_postulacion,
    )

    assert response.status_code == 200
    assert cantidad_postulaciones(app) == 0


def test_postulacion_sin_autorizacion(
    app, client, datos_postulacion
):
    datos_postulacion.pop("acepta_datos")

    response = client.post(
        "/trabaja-con-nosotros",
        data=datos_postulacion,
    )

    assert response.status_code == 200
    assert cantidad_postulaciones(app) == 0


def test_postulacion_csrf(
    app, client, datos_postulacion
):
    app.config["WTF_CSRF_ENABLED"] = True

    response = client.post(
        "/trabaja-con-nosotros",
        data=datos_postulacion,
    )

    assert response.status_code == 400
    assert cantidad_postulaciones(app) == 0

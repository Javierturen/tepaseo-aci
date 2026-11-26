from app.extensions import db
from app.models import Comuna, Servicio


def test_servicios_disponibles(client):
    response = client.get("/servicios")

    assert response.status_code == 200
    assert "Paseo básico" in response.get_data(as_text=True)
    assert "Plan mensual" in response.get_data(as_text=True)


def test_servicio_inactivo(app, client):
    with app.app_context():
        servicio = db.session.scalar(
            db.select(Servicio).filter_by(nombre="Paseo básico")
        )
        servicio.activo = False
        db.session.commit()

    response = client.get("/servicios")

    assert "Paseo básico" not in response.get_data(as_text=True)


def test_pagina_cobertura(client):
    response = client.get("/cobertura")

    assert response.status_code == 200
    assert "Providencia" in response.get_data(as_text=True)


def test_comuna_con_cobertura(app, client):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )
        comuna_id = comuna.id

    response = client.get(f"/cobertura?comuna={comuna_id}")

    assert response.status_code == 200
    assert "¡Tenemos cobertura en" in response.get_data(
        as_text=True
    )


def test_comuna_sin_cobertura(app, client):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Maipú")
        )
        comuna_id = comuna.id

    response = client.get(f"/cobertura?comuna={comuna_id}")

    assert response.status_code == 200
    assert "Actualmente no contamos con cobertura" in (
        response.get_data(as_text=True)
    )


def test_comuna_inexistente(client):
    response = client.get("/cobertura?comuna=9999")

    assert response.status_code == 200
    assert "Selecciona una comuna válida" in response.get_data(
        as_text=True
    )


def test_inicializacion_base_datos(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["init-db"])

    assert result.exit_code == 0

    with app.app_context():
        servicios = db.session.scalars(db.select(Servicio)).all()
        comunas = db.session.scalars(db.select(Comuna)).all()

        assert len(servicios) == 4
        assert len(comunas) == 6

import re
from datetime import date, time, timedelta

import pytest
from flask import template_rendered

from app.extensions import db
from app.models import (
    Administrador,
    Cliente,
    Comuna,
    Postulacion,
    Servicio,
    SolicitudPaseo,
)


CLAVE_PRUEBA = "Clave-exclusiva-de-pruebas-2026"


@pytest.fixture
def administrador(app):
    with app.app_context():
        admin = Administrador(usuario="admin")
        admin.establecer_contrasena(CLAVE_PRUEBA)

        db.session.add(admin)
        db.session.commit()

        return admin.id


@pytest.fixture
def sesion_admin(client, administrador):
    response = client.post(
        "/admin/login",
        data={
            "usuario": "admin",
            "contrasena": CLAVE_PRUEBA,
        },
    )

    assert response.status_code == 302

    return client


@pytest.fixture
def registros(app):
    with app.app_context():
        comuna = db.session.scalar(
            db.select(Comuna).filter_by(nombre="Providencia")
        )

        servicio = db.session.scalar(
            db.select(Servicio).filter_by(nombre="Paseo básico")
        )

        cliente = Cliente(
            nombre="Cliente Demo",
            correo="cliente@example.com",
            telefono="+56912345678",
        )

        solicitud = SolicitudPaseo(
            cliente=cliente,
            comuna_id=comuna.id,
            servicio_id=servicio.id,
            nombre_mascota="Max",
            raza="Labrador",
            tamano="grande",
            fecha=date.today() + timedelta(days=2),
            horario=time(10, 0),
            observaciones="Perro tranquilo.",
            acepta_datos=True,
            estado="pendiente",
        )

        postulacion = Postulacion(
            nombre="Paseador Demo",
            correo="paseador@example.com",
            telefono="+56987654321",
            comuna_id=comuna.id,
            experiencia="Experiencia cuidando perros.",
            disponibilidad="Lunes a viernes.",
            acepta_datos=True,
            estado="recibida",
        )

        db.session.add_all([solicitud, postulacion])
        db.session.commit()

        return {
            "solicitud": solicitud.id,
            "postulacion": postulacion.id,
        }


def test_contrasena_protegida(app, administrador):
    with app.app_context():
        admin = db.session.get(
            Administrador, administrador
        )

        assert admin.password_hash != CLAVE_PRUEBA
        assert admin.verificar_contrasena(CLAVE_PRUEBA)
        assert not admin.verificar_contrasena("incorrecta")


def test_crear_admin_cli(app):
    runner = app.test_cli_runner()

    resultado = runner.invoke(
        args=[
            "crear-admin",
            "--usuario", "nuevo-admin",
            "--contrasena", CLAVE_PRUEBA,
        ]
    )

    assert resultado.exit_code == 0
    assert "Administrador creado correctamente" in (
        resultado.output
    )

    with app.app_context():
        admin = db.session.scalar(
            db.select(Administrador).filter_by(
                usuario="nuevo-admin"
            )
        )

        assert admin is not None
        assert admin.verificar_contrasena(CLAVE_PRUEBA)


@pytest.mark.parametrize(
    "usuario, contrasena",
    [
        ("", CLAVE_PRUEBA),
        ("otro-admin", "123"),
        ("admin", CLAVE_PRUEBA),
    ],
)
def test_cli_rechaza_datos_invalidos(
    app, administrador, usuario, contrasena
):
    runner = app.test_cli_runner()

    resultado = runner.invoke(
        args=[
            "crear-admin",
            "--usuario", usuario,
            "--contrasena", contrasena,
        ]
    )

    assert resultado.exit_code != 0


def test_formulario_login(client):
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "Acceso administrativo" in (
        response.get_data(as_text=True)
    )


def test_login_correcto(client, administrador):
    response = client.post(
        "/admin/login",
        data={
            "usuario": "admin",
            "contrasena": CLAVE_PRUEBA,
        },
        follow_redirects=True,
    )

    contenido = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sesión iniciada correctamente" in contenido
    assert "Panel administrativo" in contenido


@pytest.mark.parametrize(
    "usuario, contrasena",
    [
        ("admin", "incorrecta"),
        ("usuario-inexistente", CLAVE_PRUEBA),
    ],
)
def test_login_invalido(
    client, administrador, usuario, contrasena
):
    response = client.post(
        "/admin/login",
        data={
            "usuario": usuario,
            "contrasena": contrasena,
        },
    )

    assert response.status_code == 200
    assert "Usuario o contraseña incorrectos" in (
        response.get_data(as_text=True)
    )

    assert client.get("/admin/").status_code == 302


def test_cierre_sesion(sesion_admin):
    response = sesion_admin.post(
        "/admin/salir",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Sesión cerrada correctamente" in (
        response.get_data(as_text=True)
    )

    assert sesion_admin.get("/admin/").status_code == 302


@pytest.mark.parametrize(
    "metodo, ruta",
    [
        ("GET", "/admin/"),
        ("GET", "/admin/solicitudes"),
        ("GET", "/admin/postulaciones"),
        ("POST", "/admin/solicitudes/1/estado"),
        ("POST", "/admin/postulaciones/1/estado"),
        ("POST", "/admin/salir"),
    ],
)
def test_rutas_privadas(client, metodo, ruta):
    response = client.open(ruta, method=metodo)

    assert response.status_code == 302
    assert "/admin/login" in response.location


def test_panel_indicadores(app, sesion_admin, registros):
    plantillas = []

    def registrar(sender, template, context, **extra):
        plantillas.append(context)

    with template_rendered.connected_to(registrar, app):
        response = sesion_admin.get("/admin/")

    assert response.status_code == 200
    assert plantillas

    contexto = plantillas[-1]

    assert contexto["total_solicitudes"] == 1
    assert contexto["pendientes"] == 1
    assert contexto["total_postulaciones"] == 1
    assert contexto["recibidas"] == 1


def test_listados_vacios(sesion_admin):
    solicitudes = sesion_admin.get("/admin/solicitudes")
    postulaciones = sesion_admin.get("/admin/postulaciones")

    assert solicitudes.status_code == 200
    assert postulaciones.status_code == 200

    assert "No existen solicitudes registradas" in (
        solicitudes.get_data(as_text=True)
    )

    assert "No existen postulaciones registradas" in (
        postulaciones.get_data(as_text=True)
    )


def test_listados_con_registros(sesion_admin, registros):
    solicitudes = sesion_admin.get("/admin/solicitudes")
    postulaciones = sesion_admin.get("/admin/postulaciones")

    assert solicitudes.status_code == 200
    assert postulaciones.status_code == 200

    assert "Cliente Demo" in (
        solicitudes.get_data(as_text=True)
    )

    assert "Max" in solicitudes.get_data(as_text=True)

    assert "Paseador Demo" in (
        postulaciones.get_data(as_text=True)
    )


@pytest.mark.parametrize(
    "inicial, destino, permitido",
    [
        ("pendiente", "confirmada", True),
        ("pendiente", "cancelada", True),
        ("confirmada", "completada", True),
        ("confirmada", "cancelada", True),
        ("pendiente", "completada", False),
        ("completada", "pendiente", False),
        ("cancelada", "confirmada", False),
        ("pendiente", "estado-inexistente", False),
    ],
)
def test_transiciones_solicitud(
    app, sesion_admin, registros, inicial, destino, permitido
):
    identificador = registros["solicitud"]

    with app.app_context():
        solicitud = db.session.get(
            SolicitudPaseo, identificador
        )
        solicitud.estado = inicial
        db.session.commit()

    response = sesion_admin.post(
        f"/admin/solicitudes/{identificador}/estado",
        data={"estado": destino},
        follow_redirects=True,
    )

    assert response.status_code == 200

    contenido = response.get_data(as_text=True)

    if permitido:
        assert "Estado de solicitud actualizado" in contenido
    else:
        assert "El cambio de estado no está permitido" in contenido

    with app.app_context():
        solicitud = db.session.get(
            SolicitudPaseo, identificador
        )

        esperado = destino if permitido else inicial

        assert solicitud.estado == esperado


@pytest.mark.parametrize(
    "inicial, destino, permitido",
    [
        ("recibida", "en revisión", True),
        ("en revisión", "aceptada", True),
        ("en revisión", "rechazada", True),
        ("recibida", "aceptada", False),
        ("aceptada", "recibida", False),
        ("rechazada", "aceptada", False),
        ("recibida", "estado-inexistente", False),
    ],
)
def test_transiciones_postulacion(
    app, sesion_admin, registros, inicial, destino, permitido
):
    identificador = registros["postulacion"]

    with app.app_context():
        postulacion = db.session.get(
            Postulacion, identificador
        )
        postulacion.estado = inicial
        db.session.commit()

    response = sesion_admin.post(
        f"/admin/postulaciones/{identificador}/estado",
        data={"estado": destino},
        follow_redirects=True,
    )

    assert response.status_code == 200

    contenido = response.get_data(as_text=True)

    if permitido:
        assert "Estado de postulación actualizado" in contenido
    else:
        assert "El cambio de estado no está permitido" in contenido

    with app.app_context():
        postulacion = db.session.get(
            Postulacion, identificador
        )

        esperado = destino if permitido else inicial

        assert postulacion.estado == esperado


@pytest.mark.parametrize(
    "ruta",
    [
        "/admin/solicitudes/9999/estado",
        "/admin/postulaciones/9999/estado",
    ],
)
def test_registro_inexistente(sesion_admin, ruta):
    response = sesion_admin.post(
        ruta,
        data={"estado": "confirmada"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "ruta",
    [
        "/admin/salir",
        "/admin/solicitudes/{solicitud}/estado",
        "/admin/postulaciones/{postulacion}/estado",
    ],
)
def test_csrf_administrativo(
    app, sesion_admin, registros, ruta
):
    app.config["WTF_CSRF_ENABLED"] = True

    response = sesion_admin.post(
        ruta.format(**registros),
        data={"estado": "confirmada"},
    )

    assert response.status_code == 400

    with app.app_context():
        solicitud = db.session.get(
            SolicitudPaseo, registros["solicitud"]
        )

        postulacion = db.session.get(
            Postulacion, registros["postulacion"]
        )

        assert solicitud.estado == "pendiente"
        assert postulacion.estado == "recibida"


def test_csrf_valido(
    app, client, administrador, registros
):
    app.config["WTF_CSRF_ENABLED"] = True

    response = client.get("/admin/login")

    token = re.search(
        r'name="csrf_token"[^>]*value="([^"]+)"',
        response.get_data(as_text=True),
    )

    assert token is not None

    response = client.post(
        "/admin/login",
        data={
            "usuario": "admin",
            "contrasena": CLAVE_PRUEBA,
            "csrf_token": token.group(1),
        },
    )

    assert response.status_code == 302

    response = client.get("/admin/solicitudes")

    token = re.search(
        r'name="csrf_token"[^>]*value="([^"]+)"',
        response.get_data(as_text=True),
    )

    assert token is not None

    identificador = registros["solicitud"]

    response = client.post(
        f"/admin/solicitudes/{identificador}/estado",
        data={
            "estado": "confirmada",
            "csrf_token": token.group(1),
        },
    )

    assert response.status_code == 302

    with app.app_context():
        solicitud = db.session.get(
            SolicitudPaseo, identificador
        )

        assert solicitud.estado == "confirmada"

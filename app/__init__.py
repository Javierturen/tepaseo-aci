import os
import secrets

import click
from flask import Flask

from app.admin import admin
from app.extensions import csrf, db, login_manager
from app.models import Administrador
from app.routes import public
from app.seed import cargar_datos


@login_manager.user_loader
def cargar_usuario(usuario_id):
    try:
        return db.session.get(
            Administrador, int(usuario_id)
        )
    except (ValueError, TypeError):
        return None


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI="sqlite:///tepaseo.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "admin.login"
    login_manager.login_message = (
        "Debes iniciar sesión para acceder al panel."
    )
    login_manager.login_message_category = "error"

    app.register_blueprint(public)
    app.register_blueprint(admin)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        cargar_datos()
        click.echo("Base de datos inicializada correctamente.")

    @app.cli.command("crear-admin")
    @click.option("--usuario", prompt="Usuario")
    @click.option(
        "--contrasena",
        prompt="Contraseña",
        hide_input=True,
        confirmation_prompt=True,
    )
    def crear_admin(usuario, contrasena):
        usuario = usuario.strip().lower()

        if not usuario or len(usuario) > 80:
            raise click.ClickException(
                "Nombre de usuario inválido."
            )

        if len(contrasena) < 12:
            raise click.ClickException(
                "La contraseña debe tener al menos 12 caracteres."
            )

        existente = db.session.scalar(
            db.select(Administrador).filter_by(usuario=usuario)
        )

        if existente:
            raise click.ClickException(
                "El administrador ya existe."
            )

        administrador = Administrador(usuario=usuario)
        administrador.establecer_contrasena(contrasena)

        db.session.add(administrador)
        db.session.commit()

        click.echo("Administrador creado correctamente.")

    return app

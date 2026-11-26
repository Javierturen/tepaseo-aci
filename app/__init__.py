import os
import secrets

import click
from flask import Flask

from app.extensions import csrf, db
from app.routes import public
from app.seed import cargar_datos


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI="sqlite:///tepaseo.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(public)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        cargar_datos()
        click.echo("Base de datos inicializada correctamente.")

    return app

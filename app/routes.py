from flask import Blueprint, render_template, request

from app.extensions import db
from app.models import Comuna, Servicio


public = Blueprint("public", __name__)


@public.route("/")
def index():
    return render_template("index.html")


@public.route("/servicios")
def servicios():
    listado = db.session.scalars(
        db.select(Servicio)
        .filter_by(activo=True)
        .order_by(Servicio.id)
    ).all()

    return render_template(
        "servicios.html", servicios=listado
    )


@public.route("/cobertura")
def cobertura():
    comunas = db.session.scalars(
        db.select(Comuna).order_by(Comuna.nombre)
    ).all()

    comuna_id = request.args.get("comuna", type=int)
    seleccionada = None

    if comuna_id is not None:
        seleccionada = db.session.get(Comuna, comuna_id)

    return render_template(
        "cobertura.html",
        comunas=comunas,
        seleccionada=seleccionada,
    )

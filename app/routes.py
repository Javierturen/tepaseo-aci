from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.forms import SolicitudPaseoForm
from app.models import Comuna, Servicio
from app.services import crear_solicitud


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


@public.route("/solicitar-paseo", methods=["GET", "POST"])
def solicitar_paseo():
    form = SolicitudPaseoForm()

    comunas = db.session.scalars(
        db.select(Comuna)
        .filter_by(activa=True)
        .order_by(Comuna.nombre)
    ).all()

    servicios = db.session.scalars(
        db.select(Servicio)
        .filter_by(activo=True)
        .order_by(Servicio.id)
    ).all()

    form.comuna.choices = [(0, "Seleccionar comuna")] + [
        (comuna.id, comuna.nombre)
        for comuna in comunas
    ]

    form.servicio.choices = [(0, "Seleccionar servicio")] + [
        (servicio.id, servicio.nombre)
        for servicio in servicios
    ]

    if form.validate_on_submit():
        crear_solicitud(form.data)

        flash(
            "Solicitud recibida correctamente. "
            "Está pendiente de confirmación.",
            "success",
        )

        return redirect(url_for("public.solicitar_paseo"))

    return render_template(
        "solicitar_paseo.html",
        form=form,
    )

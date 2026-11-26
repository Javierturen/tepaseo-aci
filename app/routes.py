from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from wtforms.fields import SelectChoice

from app.extensions import db
from app.forms import PostulacionForm, SolicitudPaseoForm
from app.models import Comuna, Servicio
from app.services import crear_postulacion, crear_solicitud


public = Blueprint("public", __name__)


def obtener_servicios_activos():
    return db.session.scalars(
        db.select(Servicio)
        .filter_by(activo=True)
        .order_by(Servicio.id)
    ).all()


@public.route("/")
def index():
    return render_template(
        "index.html",
        servicios=obtener_servicios_activos(),
    )


@public.route("/servicios")
def servicios():
    return render_template(
        "servicios.html",
        servicios=obtener_servicios_activos(),
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

    servicios = obtener_servicios_activos()

    form.comuna.choices = [
        SelectChoice("0", "Seleccionar comuna")
    ] + [
        SelectChoice(str(comuna.id), comuna.nombre)
        for comuna in comunas
    ]

    form.servicio.choices = [
        SelectChoice("0", "Seleccionar servicio")
    ] + [
        SelectChoice(str(servicio.id), servicio.nombre)
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


@public.route("/trabaja-con-nosotros", methods=["GET", "POST"])
def postulacion():
    form = PostulacionForm()

    comunas = db.session.scalars(
        db.select(Comuna).order_by(Comuna.nombre)
    ).all()

    form.comuna.choices = [
        SelectChoice("0", "Seleccionar comuna")
    ] + [
        SelectChoice(str(comuna.id), comuna.nombre)
        for comuna in comunas
    ]

    if form.validate_on_submit():
        crear_postulacion(form.data)

        flash(
            "Postulación recibida correctamente. "
            "Nuestro equipo revisará tus antecedentes.",
            "success",
        )

        return redirect(url_for("public.postulacion"))

    return render_template(
        "postulacion.html",
        form=form,
    )

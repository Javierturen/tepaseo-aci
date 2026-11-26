from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from app.admin_services import (
    TRANSICIONES_POSTULACION,
    TRANSICIONES_SOLICITUD,
    cambiar_estado_postulacion,
    cambiar_estado_solicitud,
)
from app.extensions import db
from app.models import (
    Administrador,
    Postulacion,
    SolicitudPaseo,
)


admin = Blueprint("admin", __name__, url_prefix="/admin")


class LoginForm(FlaskForm):
    usuario = StringField(
        "Usuario",
        validators=[DataRequired(), Length(max=80)],
    )

    contrasena = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(max=256)],
    )


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.panel"))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = form.usuario.data.strip().lower()

        administrador = db.session.scalar(
            db.select(Administrador).filter_by(usuario=usuario)
        )

        if administrador and administrador.verificar_contrasena(
            form.contrasena.data
        ):
            login_user(administrador)

            flash(
                "Sesión iniciada correctamente.",
                "success",
            )

            return redirect(url_for("admin.panel"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template(
        "admin_login.html",
        form=form,
    )


@admin.route("/")
@login_required
def panel():
    total_solicitudes = db.session.scalar(
        db.select(db.func.count()).select_from(SolicitudPaseo)
    )

    total_postulaciones = db.session.scalar(
        db.select(db.func.count()).select_from(Postulacion)
    )

    pendientes = db.session.scalar(
        db.select(db.func.count())
        .select_from(SolicitudPaseo)
        .where(SolicitudPaseo.estado == "pendiente")
    )

    recibidas = db.session.scalar(
        db.select(db.func.count())
        .select_from(Postulacion)
        .where(Postulacion.estado == "recibida")
    )

    return render_template(
        "admin_panel.html",
        total_solicitudes=total_solicitudes,
        total_postulaciones=total_postulaciones,
        pendientes=pendientes,
        recibidas=recibidas,
    )


@admin.route("/solicitudes")
@login_required
def solicitudes():
    registros = db.session.scalars(
        db.select(SolicitudPaseo)
        .order_by(SolicitudPaseo.id.desc())
    ).all()

    return render_template(
        "admin_solicitudes.html",
        solicitudes=registros,
        transiciones=TRANSICIONES_SOLICITUD,
    )


@admin.route(
    "/solicitudes/<int:solicitud_id>/estado",
    methods=["POST"],
)
@login_required
def actualizar_solicitud(solicitud_id):
    solicitud = db.get_or_404(
        SolicitudPaseo, solicitud_id
    )

    nuevo_estado = request.form.get("estado", "")

    if cambiar_estado_solicitud(
        solicitud, nuevo_estado
    ):
        flash(
            "Estado de solicitud actualizado correctamente.",
            "success",
        )
    else:
        flash(
            "El cambio de estado no está permitido.",
            "error",
        )

    return redirect(url_for("admin.solicitudes"))


@admin.route("/postulaciones")
@login_required
def postulaciones():
    registros = db.session.scalars(
        db.select(Postulacion)
        .order_by(Postulacion.id.desc())
    ).all()

    return render_template(
        "admin_postulaciones.html",
        postulaciones=registros,
        transiciones=TRANSICIONES_POSTULACION,
    )


@admin.route(
    "/postulaciones/<int:postulacion_id>/estado",
    methods=["POST"],
)
@login_required
def actualizar_postulacion(postulacion_id):
    postulacion = db.get_or_404(
        Postulacion, postulacion_id
    )

    nuevo_estado = request.form.get("estado", "")

    if cambiar_estado_postulacion(
        postulacion, nuevo_estado
    ):
        flash(
            "Estado de postulación actualizado correctamente.",
            "success",
        )
    else:
        flash(
            "El cambio de estado no está permitido.",
            "error",
        )

    return redirect(url_for("admin.postulaciones"))


@admin.route("/salir", methods=["POST"])
@login_required
def salir():
    logout_user()

    flash("Sesión cerrada correctamente.", "success")

    return redirect(url_for("admin.login"))

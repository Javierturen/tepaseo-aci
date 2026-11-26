import re
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.fields import SelectChoice
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    Regexp,
    ValidationError,
)


def normalizar_texto(valor):
    return (valor or "").strip()


def normalizar_telefono(valor):
    return re.sub(r"[\s()-]", "", valor or "")


class SolicitudPaseoForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        filters=[normalizar_texto],
        validators=[DataRequired(), Length(max=120)],
    )

    correo = StringField(
        "Correo electrónico",
        filters=[normalizar_texto],
        validators=[
            DataRequired(),
            Email(),
            Length(max=254),
        ],
    )

    telefono = StringField(
        "Teléfono",
        filters=[normalizar_telefono],
        validators=[
            DataRequired(),
            Regexp(
                r"^(?:\+?56)?[2-9]\d{8}$",
                message="Ingresa un teléfono chileno válido.",
            ),
        ],
    )

    nombre_mascota = StringField(
        "Nombre de tu perro",
        filters=[normalizar_texto],
        validators=[DataRequired(), Length(max=100)],
    )

    raza = StringField(
        "Raza",
        filters=[normalizar_texto],
        validators=[Optional(), Length(max=100)],
    )

    tamano = SelectField(
        "Tamaño de la mascota",
        choices=[
            SelectChoice("", "Seleccionar tamaño"),
            SelectChoice("pequeno", "Pequeño"),
            SelectChoice("mediano", "Mediano"),
            SelectChoice("grande", "Grande"),
        ],
        validators=[DataRequired()],
    )

    comuna = SelectField(
        "Comuna",
        coerce=int,
        validators=[DataRequired()],
    )

    servicio = SelectField(
        "Servicio",
        coerce=int,
        validators=[DataRequired()],
    )

    fecha = DateField(
        "Fecha solicitada",
        validators=[DataRequired()],
    )

    horario = TimeField(
        "Horario solicitado",
        validators=[DataRequired()],
    )

    observaciones = TextAreaField(
        "Observaciones adicionales",
        filters=[normalizar_texto],
        validators=[Optional(), Length(max=500)],
    )

    acepta_datos = BooleanField(
        "Autorizo el uso de mis datos para gestionar la solicitud.",
        validators=[DataRequired()],
    )

    def validate_fecha(self, campo):
        if campo.data and campo.data < date.today():
            raise ValidationError(
                "No puedes seleccionar una fecha pasada."
            )


class PostulacionForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        filters=[normalizar_texto],
        validators=[DataRequired(), Length(max=120)],
    )

    correo = StringField(
        "Correo electrónico",
        filters=[normalizar_texto],
        validators=[
            DataRequired(),
            Email(),
            Length(max=254),
        ],
    )

    telefono = StringField(
        "Teléfono",
        filters=[normalizar_telefono],
        validators=[
            DataRequired(),
            Regexp(
                r"^(?:\+?56)?[2-9]\d{8}$",
                message="Ingresa un teléfono chileno válido.",
            ),
        ],
    )

    comuna = SelectField(
        "Comuna de residencia",
        coerce=int,
        validators=[DataRequired()],
    )

    experiencia = TextAreaField(
        "Experiencia con mascotas",
        filters=[normalizar_texto],
        validators=[DataRequired(), Length(max=1000)],
    )

    disponibilidad = TextAreaField(
        "Disponibilidad horaria",
        filters=[normalizar_texto],
        validators=[DataRequired(), Length(max=500)],
    )

    acepta_datos = BooleanField(
        "Autorizo el uso de mis datos para evaluar mi postulación.",
        validators=[DataRequired()],
    )

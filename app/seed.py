from app.extensions import db
from app.models import Comuna, Servicio


def cargar_datos():
    comunas = [
        ("Providencia", True),
        ("Ñuñoa", True),
        ("Las Condes", True),
        ("Santiago", True),
        ("Maipú", False),
        ("Pudahuel", False),
    ]

    for nombre, activa in comunas:
        existente = db.session.scalar(
            db.select(Comuna).filter_by(nombre=nombre)
        )

        if existente is None:
            db.session.add(
                Comuna(nombre=nombre, activa=activa)
            )

    servicios = [
        (
            "Paseo básico",
            "Paseo individual de 30 minutos.",
            30,
            5000,
        ),
        (
            "Paseo extendido",
            "Paseo individual de 60 minutos.",
            60,
            8000,
        ),
        (
            "Plan semanal",
            "5 paseos de 30 minutos.",
            30,
            22000,
        ),
        (
            "Plan mensual",
            "20 paseos de 30 minutos.",
            30,
            80000,
        ),
    ]

    for nombre, descripcion, duracion, precio in servicios:
        existente = db.session.scalar(
            db.select(Servicio).filter_by(nombre=nombre)
        )

        if existente is None:
            db.session.add(
                Servicio(
                    nombre=nombre,
                    descripcion=descripcion,
                    duracion=duracion,
                    precio=precio,
                    activo=True,
                )
            )

    db.session.commit()

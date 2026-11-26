from app.extensions import db
from app.models import Cliente, Postulacion, SolicitudPaseo


def crear_solicitud(datos):
    cliente = Cliente(
        nombre=datos["nombre"],
        correo=datos["correo"],
        telefono=datos["telefono"],
    )

    solicitud = SolicitudPaseo(
        cliente=cliente,
        comuna_id=datos["comuna"],
        servicio_id=datos["servicio"],
        nombre_mascota=datos["nombre_mascota"],
        raza=datos["raza"],
        tamano=datos["tamano"],
        fecha=datos["fecha"],
        horario=datos["horario"],
        observaciones=datos["observaciones"],
        acepta_datos=datos["acepta_datos"],
        estado="pendiente",
    )

    db.session.add(solicitud)
    db.session.commit()

    return solicitud


def crear_postulacion(datos):
    postulacion = Postulacion(
        nombre=datos["nombre"],
        correo=datos["correo"],
        telefono=datos["telefono"],
        comuna_id=datos["comuna"],
        experiencia=datos["experiencia"],
        disponibilidad=datos["disponibilidad"],
        acepta_datos=datos["acepta_datos"],
        estado="recibida",
    )

    db.session.add(postulacion)
    db.session.commit()

    return postulacion

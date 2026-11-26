from app.extensions import db
from app.models import Cliente, SolicitudPaseo


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

from app.extensions import db


TRANSICIONES_SOLICITUD = {
    "pendiente": ("confirmada", "cancelada"),
    "confirmada": ("completada", "cancelada"),
    "completada": (),
    "cancelada": (),
}


TRANSICIONES_POSTULACION = {
    "recibida": ("en revisión",),
    "en revisión": ("aceptada", "rechazada"),
    "aceptada": (),
    "rechazada": (),
}


def cambiar_estado_solicitud(solicitud, nuevo_estado):
    permitidos = TRANSICIONES_SOLICITUD.get(
        solicitud.estado, ()
    )

    if nuevo_estado not in permitidos:
        return False

    solicitud.estado = nuevo_estado
    db.session.commit()

    return True


def cambiar_estado_postulacion(postulacion, nuevo_estado):
    permitidos = TRANSICIONES_POSTULACION.get(
        postulacion.estado, ()
    )

    if nuevo_estado not in permitidos:
        return False

    postulacion.estado = nuevo_estado
    db.session.commit()

    return True

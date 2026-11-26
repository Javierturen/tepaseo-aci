from app.extensions import db


class Comuna(db.Model):
    __tablename__ = "comunas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(
        db.String(100), unique=True, nullable=False
    )
    activa = db.Column(
        db.Boolean, default=True, nullable=False
    )


class Servicio(db.Model):
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(
        db.String(100), unique=True, nullable=False
    )
    descripcion = db.Column(db.String(250), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    activo = db.Column(
        db.Boolean, default=True, nullable=False
    )


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(254), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)


class SolicitudPaseo(db.Model):
    __tablename__ = "solicitudes_paseo"

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
    )

    comuna_id = db.Column(
        db.Integer,
        db.ForeignKey("comunas.id"),
        nullable=False,
    )

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey("servicios.id"),
        nullable=False,
    )

    nombre_mascota = db.Column(db.String(100), nullable=False)
    raza = db.Column(db.String(100))
    tamano = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    observaciones = db.Column(db.Text)
    acepta_datos = db.Column(db.Boolean, nullable=False)

    estado = db.Column(
        db.String(20),
        default="pendiente",
        nullable=False,
    )

    cliente = db.relationship("Cliente")
    comuna = db.relationship("Comuna")
    servicio = db.relationship("Servicio")

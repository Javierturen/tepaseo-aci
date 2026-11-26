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

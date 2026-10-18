from datetime import datetime
from flask_login import UserMixin
from backend.extensions import db

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(180), unique=True, nullable=False, index=True)
    rol = db.Column(db.String(24), nullable=False, default="padre", index=True)
    password_hash = db.Column(db.String(255))
    google_sub = db.Column(db.String(255), unique=True, index=True)
    proveedor = db.Column(db.String(20), nullable=False, default="local")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    @property
    def is_active(self):
        return self.activo

class Estudiante(db.Model):
    __tablename__ = "estudiantes"
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(120), nullable=False)
    apellidos = db.Column(db.String(120), nullable=False)
    codigo_interno = db.Column(db.String(40), unique=True, nullable=False, index=True)
    grado = db.Column(db.String(50), default="")
    seccion = db.Column(db.String(30), default="")
    padre_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    padre = db.relationship("Usuario", backref=db.backref("estudiantes", lazy=True))

class Expediente(db.Model):
    __tablename__ = "expedientes"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(24), unique=True, nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id"), index=True)
    nombre_solicitante = db.Column(db.String(120), nullable=False)
    documento = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    asunto = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(30), default="Recibido", nullable=False, index=True)
    observaciones = db.Column(db.Text)
    revisado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    revisado_en = db.Column(db.DateTime)
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id], backref="expedientes")
    estudiante = db.relationship("Estudiante", backref="expedientes")
    revisor = db.relationship("Usuario", foreign_keys=[revisado_por_id])
    documentos = db.relationship("Documento", backref="expediente", cascade="all, delete-orphan", lazy=True)

class Documento(db.Model):
    __tablename__ = "documentos"
    id = db.Column(db.Integer, primary_key=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey("expedientes.id"), nullable=False, index=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_guardado = db.Column(db.String(255), unique=True, nullable=False)
    tipo_mime = db.Column(db.String(120), default="application/octet-stream")
    subido_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

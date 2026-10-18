from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash
from backend.extensions import db
from backend.models import Usuario
from backend.security import roles_requeridos

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")
ROLES = {"padre", "secretaria", "personal", "administrador", "direccion"}

@usuarios_bp.route("/")
@roles_requeridos("direccion", "administrador")
def lista():
    return render_template("usuarios/lista.html", usuarios=Usuario.query.order_by(Usuario.nombre).all())

@usuarios_bp.route("/crear", methods=["GET", "POST"])
@roles_requeridos("direccion", "administrador")
def crear():
    if request.method == "POST":
        nombre=request.form.get("nombre","").strip()
        correo=request.form.get("correo","").strip().lower()
        rol=request.form.get("rol","")
        clave=request.form.get("password","")
        if not nombre or "@" not in correo or rol not in ROLES or len(clave)<12:
            flash("Revisa los datos y usa una contraseña de al menos 12 caracteres.", "error")
        elif Usuario.query.filter_by(correo=correo).first():
            flash("Ese correo ya está registrado.", "error")
        else:
            db.session.add(Usuario(nombre=nombre[:120], correo=correo, rol=rol,
                password_hash=generate_password_hash(clave)))
            db.session.commit()
            flash("Usuario creado.", "success")
            return redirect(url_for("usuarios.lista"))
    return render_template("usuarios/crear.html")

@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@roles_requeridos("direccion", "administrador")
def editar(usuario_id):
    usuario=db.get_or_404(Usuario, usuario_id)
    if request.method=="POST":
        nombre=request.form.get("nombre","").strip()
        rol=request.form.get("rol","")
        if nombre and rol in ROLES:
            usuario.nombre=nombre[:120]
            usuario.rol=rol
            db.session.commit()
            flash("Usuario actualizado.", "success")
            return redirect(url_for("usuarios.lista"))
        flash("Datos no válidos.", "error")
    return render_template("usuarios/editar.html", usuario=usuario)

@usuarios_bp.route("/<int:usuario_id>/estado", methods=["POST"])
@roles_requeridos("direccion", "administrador")
def cambiar_estado(usuario_id):
    usuario=db.get_or_404(Usuario, usuario_id)
    if usuario.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "error")
    else:
        usuario.activo=not usuario.activo
        db.session.commit()
        flash("Estado actualizado.", "success")
    return redirect(url_for("usuarios.lista"))

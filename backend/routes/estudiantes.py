import secrets
from flask import Blueprint, flash, redirect, render_template, request, url_for
from backend.extensions import db
from backend.models import Estudiante
from backend.security import roles_requeridos

estudiantes_bp = Blueprint("estudiantes", __name__, url_prefix="/estudiantes")

@estudiantes_bp.route("/")
@roles_requeridos("direccion", "administrador", "secretaria", "personal")
def lista():
    items=Estudiante.query.order_by(Estudiante.apellidos, Estudiante.nombres).all()
    return render_template("estudiantes/lista.html", estudiantes=items)

@estudiantes_bp.route("/registrar", methods=["GET", "POST"])
@roles_requeridos("direccion", "administrador", "secretaria")
def registrar():
    if request.method=="POST":
        nombres=request.form.get("nombres","").strip()
        apellidos=request.form.get("apellidos","").strip()
        if not nombres or not apellidos:
            flash("Nombres y apellidos son obligatorios.", "error")
        else:
            e=Estudiante(nombres=nombres[:120], apellidos=apellidos[:120],
                codigo_interno="AL-"+secrets.token_hex(4).upper(),
                grado=request.form.get("grado","")[:50], seccion=request.form.get("seccion","")[:30])
            db.session.add(e); db.session.commit()
            flash("Estudiante registrado. Código interno: "+e.codigo_interno, "success")
            return redirect(url_for("estudiantes.lista"))
    return render_template("estudiantes/registrar.html")

@estudiantes_bp.route("/<int:estudiante_id>")
@roles_requeridos("direccion", "administrador", "secretaria", "personal")
def detalle(estudiante_id):
    return render_template("estudiantes/detalle.html", estudiante=db.get_or_404(Estudiante, estudiante_id))

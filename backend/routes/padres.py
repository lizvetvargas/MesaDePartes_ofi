import secrets
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from backend.extensions import db
from backend.models import Estudiante, Expediente
from backend.security import roles_requeridos

padres_bp = Blueprint("padres", __name__, url_prefix="/padres")

@padres_bp.route("/")
@roles_requeridos("padre")
def dashboard():
    items = Expediente.query.filter_by(usuario_id=current_user.id).order_by(Expediente.fecha.desc()).all()
    return render_template("padres/dashboard.html", expedientes=items[:5], total=len(items),
        pendientes=sum(x.estado not in {"Atendido", "Rechazado"} for x in items),
        estudiantes=current_user.estudiantes)

@padres_bp.route("/perfil", methods=["GET", "POST"])
@roles_requeridos("padre")
def perfil():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if nombre:
            current_user.nombre = nombre[:120]
            db.session.commit()
            flash("Perfil actualizado.", "success")
            return redirect(url_for("padres.perfil"))
        flash("Escribe un nombre válido.", "error")
    return render_template("padres/perfil.html")

@padres_bp.route("/vincular-estudiante", methods=["GET", "POST"])
@roles_requeridos("padre")
def vincular_estudiante():
    if request.method == "POST":
        codigo = request.form.get("codigo_interno", "").strip()
        estudiante = Estudiante.query.filter_by(codigo_interno=codigo, activo=True).first()
        if not estudiante:
            flash("Código no encontrado. Consulta con secretaría.", "error")
        elif estudiante.padre_id not in (None, current_user.id):
            flash("La vinculación necesita revisión de secretaría.", "error")
        else:
            estudiante.padre_id = current_user.id
            db.session.commit()
            flash("Vinculación preliminar registrada. El jardín debe verificar la relación.", "success")
            return redirect(url_for("padres.dashboard"))
    return render_template("padres/vincular_estudiante.html")

@padres_bp.route("/nueva-solicitud", methods=["GET", "POST"])
@roles_requeridos("padre")
def nueva_solicitud():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        asunto = request.form.get("asunto", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estudiante_id = request.form.get("estudiante_id", type=int)
        estudiante = Estudiante.query.filter_by(id=estudiante_id, padre_id=current_user.id).first() if estudiante_id else None
        if not tipo or not asunto or (estudiante_id and not estudiante):
            flash("Completa los campos y verifica el estudiante seleccionado.", "error")
        else:
            e = Expediente(codigo="MP-" + secrets.token_hex(5).upper(), usuario_id=current_user.id,
                estudiante_id=estudiante.id if estudiante else None, nombre_solicitante=current_user.nombre,
                documento="Cuenta registrada", tipo=tipo[:80], asunto=asunto[:250],
                descripcion=descripcion, estado="Recibido")
            db.session.add(e)
            db.session.commit()
            flash("Solicitud enviada. Código: " + e.codigo, "success")
            return redirect(url_for("padres.mis_tramites"))
    return render_template("padres/nueva_solicitud.html", estudiantes=current_user.estudiantes)

@padres_bp.route("/mis-tramites")
@roles_requeridos("padre")
def mis_tramites():
    items = Expediente.query.filter_by(usuario_id=current_user.id).order_by(Expediente.fecha.desc()).all()
    return render_template("padres/mis_tramites.html", expedientes=items)

@padres_bp.route("/mis-documentos")
@roles_requeridos("padre")
def mis_documentos():
    items = Expediente.query.filter_by(usuario_id=current_user.id).order_by(Expediente.fecha.desc()).all()
    return render_template("padres/mis_documentos.html", expedientes=items)

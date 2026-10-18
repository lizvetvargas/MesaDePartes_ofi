from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from backend.extensions import db
from backend.models import Expediente
from backend.security import roles_requeridos

tramites_bp = Blueprint("tramites", __name__, url_prefix="/tramites")
PERSONAL=("direccion","administrador","secretaria","personal")

@tramites_bp.route("/")
@roles_requeridos(*PERSONAL)
def lista():
    estado=request.args.get("estado","").strip()
    q=Expediente.query
    if estado: q=q.filter_by(estado=estado)
    return render_template("tramites/lista.html", expedientes=q.order_by(Expediente.fecha.desc()).all(), estado=estado)

@tramites_bp.route("/<int:expediente_id>")
@roles_requeridos(*PERSONAL)
def detalle(expediente_id):
    return render_template("tramites/detalle.html", expediente=db.get_or_404(Expediente, expediente_id), consulta_publica=False)

@tramites_bp.route("/<int:expediente_id>/revisar", methods=["GET","POST"])
@roles_requeridos(*PERSONAL)
def revisar(expediente_id):
    e=db.get_or_404(Expediente, expediente_id)
    if request.method=="POST":
        estado=request.form.get("estado","")
        if estado not in {"Recibido","En revisión","Observado","Atendido","Rechazado"}:
            flash("Estado no válido.", "error")
        else:
            e.estado=estado
            e.observaciones=request.form.get("observaciones","").strip()
            e.revisado_por_id=current_user.id
            e.revisado_en=datetime.utcnow()
            db.session.commit()
            flash("Trámite actualizado.", "success")
            return redirect(url_for("tramites.detalle", expediente_id=e.id))
    return render_template("tramites/revisar.html", expediente=e)

@tramites_bp.route("/consultar", methods=["GET","POST"])
def consultar():
    e=None; buscado=False; codigo=""; documento=""
    if request.method=="POST":
        codigo=request.form.get("codigo","").strip().upper()
        documento=request.form.get("documento","").strip()
        buscado=True
        e=Expediente.query.filter_by(codigo=codigo, documento=documento).first()
    return render_template("tramites/consulta.html", expediente=e, busqueda_realizada=buscado, codigo=codigo, documento=documento)

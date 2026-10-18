from pathlib import Path
from uuid import uuid4
from flask import Blueprint, abort, current_app, flash, redirect, request, send_from_directory, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models import Documento, Expediente
from backend.security import roles_requeridos

documentos_bp=Blueprint("documentos", __name__, url_prefix="/documentos")
ALLOWED={"pdf","png","jpg","jpeg"}
STAFF={"direccion","administrador","secretaria","personal"}

@documentos_bp.route("/subir/<int:expediente_id>", methods=["POST"])
@roles_requeridos("direccion","administrador","secretaria","personal","padre")
def subir(expediente_id):
    e=db.get_or_404(Expediente, expediente_id)
    if current_user.rol not in STAFF and e.usuario_id != current_user.id: abort(403)
    f=request.files.get("archivo")
    if not f or not f.filename:
        flash("Selecciona un archivo.", "error")
        return redirect(url_for("padres.mis_tramites") if current_user.rol=="padre" else url_for("tramites.detalle", expediente_id=e.id))
    name=secure_filename(f.filename)
    if "." not in name or name.rsplit(".",1)[1].lower() not in ALLOWED:
        flash("Solo se permiten archivos PDF, PNG y JPG.", "error")
        return redirect(url_for("padres.mis_tramites") if current_user.rol=="padre" else url_for("tramites.detalle", expediente_id=e.id))
    ext=name.rsplit(".",1)[1].lower()
    saved=f"{uuid4().hex}.{ext}"
    folder=Path(current_app.instance_path)/"documentos_privados"
    folder.mkdir(parents=True, exist_ok=True)
    f.save(folder/saved)
    db.session.add(Documento(expediente_id=e.id, nombre_original=name[:255], nombre_guardado=saved, tipo_mime=f.mimetype or "application/octet-stream"))
    db.session.commit()
    flash("Documento adjuntado.", "success")
    return redirect(url_for("padres.mis_tramites") if current_user.rol=="padre" else url_for("tramites.detalle", expediente_id=e.id))

@documentos_bp.route("/descargar/<int:documento_id>")
@roles_requeridos("direccion","administrador","secretaria","personal","padre")
def descargar(documento_id):
    d=db.get_or_404(Documento, documento_id)
    if current_user.rol not in STAFF and d.expediente.usuario_id != current_user.id: abort(403)
    folder=Path(current_app.instance_path)/"documentos_privados"
    return send_from_directory(folder, d.nombre_guardado, as_attachment=True, download_name=d.nombre_original)

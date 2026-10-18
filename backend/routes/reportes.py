from flask import Blueprint, render_template
from backend.models import Usuario, Estudiante, Expediente
from backend.security import roles_requeridos
reportes_bp=Blueprint("reportes", __name__)

def dashboard(es_direccion=False):
    return render_template("admin/dashboard.html",
        total_tramites=Expediente.query.count(),
        pendientes=Expediente.query.filter(Expediente.estado.in_({"Recibido","En revisión","Observado"})).count(),
        total_estudiantes=Estudiante.query.count(), total_usuarios=Usuario.query.count(),
        es_direccion=es_direccion)

@reportes_bp.route("/admin")
@roles_requeridos("administrador","secretaria","personal")
def admin_dashboard(): return dashboard()

@reportes_bp.route("/direccion")
@roles_requeridos("direccion")
def direccion_dashboard(): return dashboard(True)

@reportes_bp.route("/admin/configuracion")
@roles_requeridos("direccion","administrador")
def configuracion(): return render_template("admin/configuracion.html")

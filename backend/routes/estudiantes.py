import secrets

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Estudiante
from backend.security import roles_requeridos


estudiantes_bp = Blueprint(
    "estudiantes",
    __name__,
    url_prefix="/estudiantes",
)

EDADES = ("3 años", "4 años", "5 años")
AULAS_SUGERIDAS = ("Azul", "Amarilla", "Verde")


def validar_datos_estudiante(estudiante_id=None):
    datos = {
        "nombres": request.form.get("nombres", "").strip(),
        "apellidos": request.form.get("apellidos", "").strip(),
        "dni": request.form.get("dni", "").strip(),
        "codigo_matricula": request.form.get(
            "codigo_matricula", ""
        ).strip(),
        "nivel": request.form.get("nivel", "Inicial").strip(),
        "grado": request.form.get("grado", "").strip(),
        "aula": request.form.get("aula", "").strip(),
        "seccion": request.form.get("seccion", "").strip(),
    }

    errores = []

    if not datos["nombres"] or not datos["apellidos"]:
        errores.append("Nombres y apellidos son obligatorios.")

    if len(datos["nombres"]) > 120 or len(datos["apellidos"]) > 120:
        errores.append("Nombres y apellidos admiten hasta 120 caracteres.")

    dni = datos["dni"]
    if not dni.isdigit() or len(dni) != 8:
        errores.append("El DNI debe contener exactamente 8 dígitos.")
    else:
        consulta = Estudiante.query.filter_by(dni=dni)
        if estudiante_id is not None:
            consulta = consulta.filter(Estudiante.id != estudiante_id)
        if consulta.first():
            errores.append("Ya existe un estudiante con ese DNI.")

    if datos["grado"] not in EDADES:
        errores.append("Selecciona una edad: 3, 4 o 5 años.")

    if datos["nivel"] != "Inicial":
        errores.append("El nivel educativo debe ser Inicial.")

    codigo = datos["codigo_matricula"]
    if len(codigo) > 50:
        errores.append("El código de matrícula es demasiado largo.")
    elif codigo:
        consulta = Estudiante.query.filter_by(codigo_matricula=codigo)
        if estudiante_id is not None:
            consulta = consulta.filter(Estudiante.id != estudiante_id)
        if consulta.first():
            errores.append("El código de matrícula ya está registrado.")

    if len(datos["aula"]) > 30 or len(datos["seccion"]) > 30:
        errores.append("Aula y sección admiten hasta 30 caracteres.")

    if errores:
        for error in errores:
            flash(error, "error")
        return None

    datos["codigo_matricula"] = codigo or None
    return datos


@estudiantes_bp.route("/")
@roles_requeridos(
    "direccion", "administrador", "secretaria", "personal"
)
def lista():
    estudiantes = Estudiante.query.order_by(
        Estudiante.apellidos,
        Estudiante.nombres,
    ).all()

    return render_template(
        "estudiantes/lista.html",
        estudiantes=estudiantes,
    )


@estudiantes_bp.route("/registrar", methods=["GET", "POST"])
@roles_requeridos("direccion", "administrador", "secretaria")
def registrar():
    if request.method == "POST":
        datos = validar_datos_estudiante()

        if datos is not None:
            estudiante = Estudiante(
                **datos,
                codigo_interno="AL-" + secrets.token_hex(4).upper(),
            )

            try:
                db.session.add(estudiante)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(
                    "No se pudo guardar. Verifica el DNI y el código "
                    "de matrícula.",
                    "error",
                )
            else:
                flash(
                    "Estudiante registrado. Código interno: "
                    + estudiante.codigo_interno,
                    "success",
                )
                return redirect(url_for("estudiantes.lista"))

    return render_template(
        "estudiantes/registrar.html",
        edades=EDADES,
        aulas=AULAS_SUGERIDAS,
    )


@estudiantes_bp.route("/<int:estudiante_id>")
@roles_requeridos(
    "direccion", "administrador", "secretaria", "personal"
)
def detalle(estudiante_id):
    estudiante = db.get_or_404(Estudiante, estudiante_id)

    return render_template(
        "estudiantes/detalle.html",
        estudiante=estudiante,
    )


@estudiantes_bp.route(
    "/<int:estudiante_id>/editar",
    methods=["GET", "POST"],
)
@roles_requeridos("direccion", "administrador", "secretaria")
def editar(estudiante_id):
    estudiante = db.get_or_404(Estudiante, estudiante_id)

    if request.method == "POST":
        datos = validar_datos_estudiante(estudiante.id)

        if datos is not None:
            for campo, valor in datos.items():
                setattr(estudiante, campo, valor)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(
                    "No se pudieron guardar los cambios. "
                    "Verifica el DNI y el código de matrícula.",
                    "error",
                )
            else:
                flash(
                    "Los datos del estudiante se actualizaron correctamente.",
                    "success",
                )
                return redirect(
                    url_for(
                        "estudiantes.detalle",
                        estudiante_id=estudiante.id,
                    )
                )

    return render_template(
        "estudiantes/editar.html",
        estudiante=estudiante,
        edades=EDADES,
        aulas=AULAS_SUGERIDAS,
    )

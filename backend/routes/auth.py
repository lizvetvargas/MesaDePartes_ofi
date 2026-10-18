from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from backend.extensions import db, oauth
from backend.models import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.record_once
def setup_google(state):
    app = state.app
    if app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"):
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

@auth_bp.route("/padres", methods=["GET", "POST"])
def login_padres():
    return login_form("padre", "Ingreso para padres de familia")

@auth_bp.route("/personal", methods=["GET", "POST"])
def login_personal():
    return login_form("personal", "Ingreso del personal administrativo")

@auth_bp.route("/direccion", methods=["GET", "POST"])
def login_direccion():
    return login_form("direccion", "Ingreso de dirección")

def login_form(tipo, titulo):
    if current_user.is_authenticated:
        return panel_por_rol(current_user.rol)
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("password", "")
        usuario = Usuario.query.filter_by(correo=correo).first()
        roles = {"padre"} if tipo == "padre" else (
            {"direccion"} if tipo == "direccion" else {"administrador", "secretaria", "personal"}
        )
        if usuario and usuario.activo and usuario.rol in roles and usuario.password_hash and check_password_hash(usuario.password_hash, clave):
            login_user(usuario)
            return panel_por_rol(usuario.rol)
        flash("No se pudo iniciar sesión. Revisa tus datos y el tipo de acceso.", "error")
    return render_template("auth/login.html", titulo=titulo, tipo=tipo)

@auth_bp.route("/google")
def google_login():
    tipo = request.args.get("tipo", "padres")
    if tipo not in {"padres", "personal", "direccion"}:
        abort(400)
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("El acceso con Google requiere configurar las credenciales en .env.", "error")
        return redirect(url_for({"padres":"auth.login_padres","personal":"auth.login_personal","direccion":"auth.login_direccion"}[tipo]))
    client = oauth.create_client("google")
    return client.authorize_redirect(current_app.config["GOOGLE_REDIRECT_URI"], prompt="select_account")

@auth_bp.route("/google/callback")
def google_callback():
    client = oauth.create_client("google")
    if client is None:
        abort(503)
    token = client.authorize_access_token()
    info = token.get("userinfo") or client.userinfo()
    correo = (info.get("email") or "").strip().lower()
    subject = info.get("sub")
    if not correo or not subject or not info.get("email_verified"):
        flash("Google no verificó el correo de la cuenta.", "error")
        return redirect(url_for("inicio"))
    usuario = Usuario.query.filter((Usuario.google_sub == subject) | (Usuario.correo == correo)).first()
    if not usuario or not usuario.activo:
        flash("La cuenta de Google aún no está habilitada por el jardín.", "error")
        return redirect(url_for("inicio"))
    if not usuario.google_sub:
        usuario.google_sub = subject
        usuario.proveedor = "google"
        db.session.commit()
    login_user(usuario)
    return panel_por_rol(usuario.rol)

@auth_bp.route("/salir", methods=["POST"])
def salir():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("inicio"))

def panel_por_rol(rol):
    if rol == "padre":
        return redirect(url_for("padres.dashboard"))
    if rol in {"administrador", "secretaria", "personal"}:
        return redirect(url_for("reportes.admin_dashboard"))
    if rol == "direccion":
        return redirect(url_for("reportes.direccion_dashboard"))
    abort(403)

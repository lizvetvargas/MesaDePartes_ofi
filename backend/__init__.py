from pathlib import Path
from flask import Flask, render_template
from config import Config
from backend.extensions import db, login_manager, csrf, oauth

def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path, "documentos_privados").mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = "auth.login_padres"
    login_manager.login_message = "Inicia sesión para continuar."

    from backend import models
    from backend.routes.auth import auth_bp
    from backend.routes.padres import padres_bp
    from backend.routes.usuarios import usuarios_bp
    from backend.routes.estudiantes import estudiantes_bp
    from backend.routes.tramites import tramites_bp
    from backend.routes.documentos import documentos_bp
    from backend.routes.reportes import reportes_bp
    for bp in (auth_bp, padres_bp, usuarios_bp, estudiantes_bp, tramites_bp, documentos_bp, reportes_bp):
        app.register_blueprint(bp)

    @app.route("/")
    def inicio():
        return render_template("inicio.html")

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("error.html", codigo=403, mensaje="No tienes permisos para acceder a esta sección."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", codigo=404, mensaje="La página solicitada no existe."), 404

    @app.errorhandler(413)
    def too_large(_e):
        return render_template("error.html", codigo=413, mensaje="El archivo supera el límite de 8 MB."), 413

    @app.cli.command("crear-tablas")
    def crear_tablas():
        with app.app_context():
            db.create_all()
        print("Tablas creadas sin borrar las existentes.")

    @app.cli.command("crear-direccion")
    def crear_direccion():
        from getpass import getpass
        from werkzeug.security import generate_password_hash
        from backend.models import Usuario
        correo = input("Correo institucional de dirección: ").strip().lower()
        if Usuario.query.filter_by(correo=correo).first():
            print("Ya existe una cuenta con ese correo.")
            return
        nombre = input("Nombre: ").strip()
        clave = getpass("Contraseña (mínimo 12 caracteres): ")
        if len(clave) < 12:
            print("La contraseña debe tener al menos 12 caracteres.")
            return
        usuario = Usuario(nombre=nombre, correo=correo, rol="direccion",
                          password_hash=generate_password_hash(clave), proveedor="local")
        db.session.add(usuario)
        db.session.commit()
        print("Cuenta de dirección creada.")
    return app

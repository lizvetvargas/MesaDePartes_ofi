from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()

@login_manager.user_loader
def load_user(user_id):
    from backend.models import Usuario
    try:
        return db.session.get(Usuario, int(user_id))
    except (ValueError, TypeError):
        return None

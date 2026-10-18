from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def roles_requeridos(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.activo:
                abort(403)
            if current_user.rol not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

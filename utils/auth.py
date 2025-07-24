from functools import wraps
from flask import request, redirect, url_for, flash
import os
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALG = 'HS256'


def generate_token(payload, expires_in=3600):
    import datetime
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(role=None):
    """
    Decorator to require login.

    :param role: None (any logged-in user allowed),
                 str role e.g. 'customer' or 'banker',
                 or list of roles allowed.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('access_token')
            payload = verify_token(token)
            if not payload:
                flash("Unauthorized. Please log in.", "danger")
                return redirect(url_for('auth.login'))

            if role:
                allowed_roles = role if isinstance(role, list) else [role]
                if payload.get('role') not in allowed_roles:
                    flash("Unauthorized. Please log in.", "danger")
                    return redirect(url_for('auth.login'))

            return f(payload, *args, **kwargs)

        return decorated_function
    return decorator

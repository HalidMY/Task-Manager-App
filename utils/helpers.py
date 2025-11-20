from functools import wraps
from flask import redirect, url_for, flash, session


def login_required(redirect_to=("login")):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page", "warning")
                return redirect(url_for(redirect_to))
            return f(*args, **kwargs)
        return decorated
    return wrapper
from flask_login import current_user
from functools import wraps
from flask import flash, redirect, url_for,abort


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated or current_user.is_admin != True:
            return abort(403)
            # flash("You need to be an admin to view this page.")
            # return redirect(url_for('products_bp.home'))
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function



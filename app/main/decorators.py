from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def required_access(people):
    def iteration(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.USERTYPE not in people:
                flash("You do not have access to this page! Please check your login info.")
                print('dont have access')
                return redirect(url_for('auth.login'))
            else:
                print('have access')
            return func(*args, **kwargs)
        return decorated_function
    return iteration

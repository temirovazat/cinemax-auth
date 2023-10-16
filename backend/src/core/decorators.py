from functools import wraps
from typing import Callable

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from werkzeug.exceptions import Forbidden

from core.enums import AuthRoles


def admin_required(view: Callable) -> Callable:
    """
    Decorate a function to restrict access to administrators only.

    Args:
        view: The function representing the resource.

    Returns:
        Callable: The decorated function.
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if AuthRoles.ADMIN.value not in claims['roles']:
            raise Forbidden('Available only to administrators')
        return view(*args, **kwargs)
    return wrapper

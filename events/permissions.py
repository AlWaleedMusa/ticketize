from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render


def roles_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")
            if request.user.role not in allowed_roles:
                return render(request, "events/forbidden.html")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

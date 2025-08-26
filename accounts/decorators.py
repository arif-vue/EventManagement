from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*roles):
    """
    Decorator that checks if user has any of the specified roles.
    Usage: @role_required('Admin', 'Organizer')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=roles).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator that requires Admin role"""
    return role_required('Admin')(view_func)

def organizer_required(view_func):
    """Decorator that requires Organizer or Admin role"""
    return role_required('Admin', 'Organizer')(view_func)

def participant_required(view_func):
    """Decorator that requires at least Participant role (all authenticated users)"""
    return role_required('Admin', 'Organizer', 'Participant')(view_func)

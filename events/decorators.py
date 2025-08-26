from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Check if user is in Admin group
        if not request.user.groups.filter(name='Admin').exists():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('event_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def organizer_required(view_func):
    """Decorator to require organizer or admin role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Check if user is in Admin or Organizer group
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(group in ['Admin', 'Organizer'] for group in user_groups):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('event_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def participant_required(view_func):
    """Decorator to require participant role (any authenticated user)"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # All authenticated users can be participants
        return view_func(request, *args, **kwargs)
    return wrapper

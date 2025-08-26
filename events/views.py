from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User, Group
from .models import Event, Category, RSVP, UserProfile
from .forms import EventForm, CategoryForm, RSVPForm, UserRoleForm
from .decorators import admin_required, organizer_required

@login_required
def dashboard(request):
    """User dashboard based on role using Django Groups"""
    user = request.user
    
    # Check user groups for role-based redirection
    if user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    else:
        # Default to participant dashboard if no group assigned
        # Also assign participant group to users without groups
        participant_group, created = Group.objects.get_or_create(name='Participant')
        user.groups.add(participant_group)
        return redirect('participant_dashboard')

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive statistics"""
    total_events = Event.objects.count()
    total_categories = Category.objects.count()
    total_rsvps = RSVP.objects.count()
    
    recent_events = Event.objects.order_by('-created_at')[:5]
    recent_rsvps = RSVP.objects.select_related('user', 'event').order_by('-rsvp_date')[:10]
    
    context = {
        'total_events': total_events,
        'total_categories': total_categories,
        'total_rsvps': total_rsvps,
        'recent_events': recent_events,
        'recent_rsvps': recent_rsvps,
        'user_role': 'Admin'
    }
    return render(request, 'events/admin_dashboard.html', context)

@login_required
@organizer_required
def organizer_dashboard(request):
    """Organizer dashboard with their events"""
    user_events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    total_participants = RSVP.objects.filter(event__created_by=request.user, response='attending').count()
    
    context = {
        'user_events': user_events,
        'total_participants': total_participants,
        'user_role': 'Organizer'
    }
    return render(request, 'events/organizer_dashboard.html', context)

@login_required
def participant_dashboard(request):
    """Participant dashboard with their RSVPs"""
    user_rsvps = RSVP.objects.filter(user=request.user).select_related('event').order_by('-rsvp_date')
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
    
    context = {
        'user_rsvps': user_rsvps,
        'upcoming_events': upcoming_events,
        'user_role': 'Participant'
    }
    return render(request, 'events/participant_dashboard.html', context)

def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = None
    can_rsvp = False
    
    if request.user.is_authenticated:
        try:
            user_rsvp = RSVP.objects.get(user=request.user, event=event)
        except RSVP.DoesNotExist:
            pass
        
        # Check if user can RSVP (not full and not already attending)
        can_rsvp = (
            not event.is_full and 
            (user_rsvp is None or user_rsvp.response != 'attending')
        )
    
    context = {
        'event': event,
        'user_rsvp': user_rsvp,
        'can_rsvp': can_rsvp,
        'rsvp_list': RSVP.objects.filter(event=event, response='attending').select_related('user')
    }
    return render(request, 'events/event_detail.html', context)

@login_required
@require_POST
def rsvp_event(request, pk):
    """Handle RSVP to an event"""
    event = get_object_or_404(Event, pk=pk)
    
    # Check if event is full
    if event.is_full:
        messages.error(request, 'This event is full and cannot accept more participants.')
        return redirect('event_detail', pk=pk)
    
    # Get or create RSVP
    rsvp, created = RSVP.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={'response': 'attending', 'notes': request.POST.get('notes', '')}
    )
    
    if not created:
        # Update existing RSVP
        rsvp.response = 'attending'
        rsvp.notes = request.POST.get('notes', '')
        rsvp.save()
        messages.success(request, f'Your RSVP for "{event.name}" has been updated!')
    else:
        messages.success(request, f'You have successfully RSVP\'d to "{event.name}"!')
    
    # Send confirmation email
    try:
        send_rsvp_confirmation_email(request.user, event, rsvp)
    except Exception as e:
        messages.warning(request, 'RSVP recorded but confirmation email could not be sent.')
    
    return redirect('event_detail', pk=pk)

@login_required
@require_POST
def cancel_rsvp(request, pk):
    """Cancel RSVP to an event"""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        rsvp = RSVP.objects.get(user=request.user, event=event)
        rsvp.response = 'not_attending'
        rsvp.save()
        messages.success(request, f'Your RSVP for "{event.name}" has been cancelled.')
    except RSVP.DoesNotExist:
        messages.error(request, 'No RSVP found to cancel.')
    
    return redirect('event_detail', pk=pk)

def send_rsvp_confirmation_email(user, event, rsvp):
    """Send RSVP confirmation email"""
    subject = f'RSVP Confirmation - {event.name}'
    html_message = render_to_string('events/emails/rsvp_confirmation.html', {
        'user': user,
        'event': event,
        'rsvp': rsvp,
        'event_url': f"http://127.0.0.1:8000{reverse('event_detail', args=[event.pk])}"
    })
    
    send_mail(
        subject=subject,
        message='',  # Plain text version (empty for now)
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

@login_required
@organizer_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@login_required
@organizer_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is the creator or admin
    is_admin = request.user.groups.filter(name='Admin').exists()
    if event.created_by != request.user and not is_admin:
        messages.error(request, 'You can only edit events you created.')
        return redirect('event_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})

@login_required
@organizer_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # Check if user is the creator or admin
    is_admin = request.user.groups.filter(name='Admin').exists()
    if event.created_by != request.user and not is_admin:
        messages.error(request, 'You can only delete events you created.')
        return redirect('event_detail', pk=pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'events/category_list.html', {'categories': categories})

@login_required
@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'events/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
def participant_list(request, pk):
    event = get_object_or_404(Event, pk=pk)
    rsvps = RSVP.objects.filter(event=event, response='attending').select_related('user')
    return render(request, 'events/participant_list.html', {'event': event, 'rsvps': rsvps})
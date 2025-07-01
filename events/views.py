from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm

def dashboard(request):
    # Stats calculations
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    today = timezone.now().date()
    
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    
    # Today's events with optimized queries
    todays_events = Event.objects.filter(date=today).select_related('category')
    
    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'todays_events': todays_events
    }
    return render(request, 'events/dashboard.html', context)

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('category').prefetch_related('participants')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Date range filter
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        return queryset.annotate(participant_count=Count('participants'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related('participants')

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = '/events/'

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = '/events/'

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = '/events/'

class ParticipantListView(ListView):
    model = Participant
    template_name = 'events/participant_list.html'
    context_object_name = 'participants'

class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    success_url = '/participants/'

class ParticipantUpdateView(UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    success_url = '/participants/'

class ParticipantDeleteView(DeleteView):
    model = Participant
    template_name = 'events/participant_confirm_delete.html'
    success_url = '/participants/'

class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = '/categories/'

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = '/categories/'

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    success_url = '/categories/'
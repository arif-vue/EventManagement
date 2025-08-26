from django.urls import path
from . import views

urlpatterns = [
    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('participant-dashboard/', views.participant_dashboard, name='participant_dashboard'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # RSVP URLs
    path('events/<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/<int:pk>/cancel-rsvp/', views.cancel_rsvp, name='cancel_rsvp'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # Participant URLs
    path('events/<int:pk>/participants/', views.participant_list, name='participant_list'),
]
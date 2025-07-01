from django.urls import path
from .views import (
    dashboard,
    EventListView, EventDetailView, EventCreateView, EventUpdateView, EventDeleteView,
    ParticipantListView, ParticipantCreateView, ParticipantUpdateView, ParticipantDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    
    # Event URLs
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/create/', EventCreateView.as_view(), name='event-create'),
    path('events/<int:pk>/update/', EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    
    # Participant URLs
    path('participants/', ParticipantListView.as_view(), name='participant-list'),
    path('participants/create/', ParticipantCreateView.as_view(), name='participant-create'),
    path('participants/<int:pk>/update/', ParticipantUpdateView.as_view(), name='participant-update'),
    path('participants/<int:pk>/delete/', ParticipantDeleteView.as_view(), name='participant-delete'),
    
    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
]
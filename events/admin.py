from django.contrib import admin
from django.contrib.auth.models import User
from .models import Event, Category, UserProfile, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'time', 'location', 'category', 'created_by']
    list_filter = ['date', 'category', 'created_by']
    search_fields = ['name', 'location', 'description']
    date_hierarchy = 'date'
    filter_horizontal = ['participants']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_activated', 'created_at']
    list_filter = ['is_activated', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'response', 'rsvp_date']
    list_filter = ['response', 'rsvp_date', 'event']
    search_fields = ['user__username', 'user__email', 'event__name']
    readonly_fields = ['rsvp_date']
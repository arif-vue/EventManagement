from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_categories', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category-list')

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)
    rsvp_participants = models.ManyToManyField(User, through='RSVP', related_name='rsvp_events', blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of participants (leave blank for unlimited)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-time']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})
    
    @property
    def rsvp_count(self):
        return self.rsvp_participants.count()
    
    @property
    def is_full(self):
        if self.max_participants:
            return self.rsvp_count >= self.max_participants
        return False
    
    @property
    def available_spots(self):
        if self.max_participants:
            return max(0, self.max_participants - self.rsvp_count)
        return None

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_activated = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} Profile"

class RSVP(models.Model):
    """Model to track RSVP responses for events"""
    RSVP_CHOICES = [
        ('attending', 'Attending'),
        ('not_attending', 'Not Attending'),
        ('maybe', 'Maybe'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    response = models.CharField(max_length=20, choices=RSVP_CHOICES, default='attending')
    rsvp_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes from the participant")
    
    class Meta:
        unique_together = ('user', 'event')  # Ensure one RSVP per user per event
        ordering = ['-rsvp_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.response})"
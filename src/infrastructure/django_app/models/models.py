"""
Django ORM Models for Event Management System.
"""
from django.db import models
from django.utils import timezone


class EventModel(models.Model):
    """Django model for Event entity."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    id = models.CharField(max_length=36, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    max_participants = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"


class ParticipantModel(models.Model):
    """Django model for Participant entity."""

    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'participants'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class EventParticipantModel(models.Model):
    """Django model for many-to-many relationship between events and participants."""

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(EventModel, on_delete=models.CASCADE)
    participant = models.ForeignKey(ParticipantModel, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'event_participants'
        unique_together = ['event', 'participant']
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.participant.name} -> {self.event.title}"
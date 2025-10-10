import uuid
from django.db import models
from django.utils import timezone


class Session(models.Model):
    """Chat session model to track conversations."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.id}"


class Message(models.Model):
    """Individual messages within a chat session."""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.text[:50]}..."


class Lead(models.Model):
    """Qualified leads extracted from conversations."""
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    interest_score = models.FloatField(default=0.0)
    source_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='leads')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lead: {self.name or 'Unknown'} ({self.email or 'No email'})"




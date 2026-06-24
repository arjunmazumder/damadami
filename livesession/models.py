import uuid
from django.db import models
from user.models import User
from tag.models import AdminTag

class CallSession(models.Model):
    STATUS_CHOICES = [
        ('searching', 'Searching'),
        ('connected', 'Connected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('timeout', 'Timeout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_calls')
    tag = models.ForeignKey(AdminTag, on_delete=models.CASCADE, related_name='calls')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='searching')
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_calls')
    rejected_vendors = models.ManyToManyField(User, related_name='rejected_calls', blank=True)
    channel_name = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Call {self.id} - {self.status}"

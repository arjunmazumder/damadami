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
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_calls')
    channel_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Call {self.id} - {self.status}"

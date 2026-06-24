import uuid
from django.db import models

class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        'lookup.Lookup',
        on_delete=models.CASCADE,
        related_name='permissions',
        limit_choices_to={'name': 'role', 'is_active': True}
    )
    permission_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-create_at']

    def __str__(self):
        return f"{self.role} - {self.permission_name}"




import uuid
from django.db import models

class AdminTag(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tagname    = models.CharField(max_length=100, unique=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.tagname

class VendorTag(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor     = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='vendor_tags')
    admin_tag  = models.ForeignKey(AdminTag, on_delete=models.CASCADE, related_name='vendor_usages')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('vendor', 'admin_tag')

    def __str__(self):
        return f"{self.vendor.email} - {self.admin_tag.tagname}"


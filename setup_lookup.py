import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from lookup.models import Lookup

# Create a lookup for role
role, created = Lookup.objects.get_or_create(
    name='role',
    value='Admin',
    defaults={'is_active': True}
)

print(f"Role '{role.value}' created with ID: {role.id}")

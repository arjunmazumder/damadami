import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from lookup.models import Lookup

roles = ['Admin', 'Vendor', 'Buyer']

for role_value in roles:
    role_obj, created = Lookup.objects.get_or_create(
        name='role',
        value=role_value,
        defaults={'is_active': True}
    )
    if created:
        print(f"Role '{role_value}' created with ID: {role_obj.id}")
    else:
        print(f"Role '{role_value}' already exists with ID: {role_obj.id}")

print("\n--- Current Roles in Database ---")
for r in Lookup.objects.filter(name='role'):
    print(f"{r.value}: {r.id}")

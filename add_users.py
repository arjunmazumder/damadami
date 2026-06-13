import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from user.models import User
from lookup.models import Lookup

roles = {
    'Admin': 'admin@gmail.com',
    'Vendor': 'vendor@gmail.com',
    'Buyer': 'buyer@gmail.com'
}

print("--- Registering Users ---")
for role_value, email in roles.items():
    role_obj = Lookup.objects.filter(name='role', value=role_value).first()
    
    if role_obj:
        user, created = User.objects.get_or_create(
            email=email, 
            defaults={
                'role': role_obj,
                'name': f"{role_value} User",
                'phone_number': '01700000000',
                'present_address': 'Dhaka',
                'permanent_address': 'Dhaka',
            }
        )
        if created:
            user.set_password('123456') # Setting a common password
            user.save()
            print(f"Created {role_value} user -> Email: {email} | Password: '123456' | ID: {user.id}")
        else:
            print(f"{role_value} user already exists -> Email: {email} | ID: {user.id}")
    else:
        print(f"Error: Role {role_value} not found in database!")

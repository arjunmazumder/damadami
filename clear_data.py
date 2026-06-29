import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damadami.settings')
django.setup()

from django.apps import apps
from user.models import User

# List of your project's apps whose data should be cleared
app_labels_to_clear = ['tag', 'permission', 'paymentgateway', 'livesession', 'invoice', 'crm', 'user']

for app_label in app_labels_to_clear:
    app_config = apps.get_app_config(app_label)
    for model in app_config.get_models():
        if model == User:
            # Keep superusers so you can still log into the admin panel
            count, _ = model.objects.filter(is_superuser=False).delete()
            print(f"Deleted {count} non-superuser Users from {app_label}")
        else:
            count, _ = model.objects.all().delete()
            print(f"Deleted {count} records from {model.__name__} in {app_label}")

print("Data cleanup complete. Lookup data and Superusers are preserved.")

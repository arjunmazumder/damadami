import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "damadami.settings")
django.setup()

from django.test import Client
from user.models import User

# Create a test user
User.objects.filter(email="test@example.com").delete()
user = User.objects.create_user(email="test@example.com", password="password123")

client = Client()

# Test Login
print("Testing Login...")
response = client.post('/auth/login', {'email': 'test@example.com', 'password': 'password123'}, content_type='application/json')
print(f"Login Status: {response.status_code}")
data = response.json()
print(f"Access Token: {data.get('access_token')[:20]}...")
refresh_token = response.cookies.get('refresh_token')
print(f"Refresh Token cookie set: {refresh_token is not None}")

# Test Refresh
print("\nTesting Refresh...")
response = client.post('/auth/getRefreshToken')
print(f"Refresh Status: {response.status_code}")
data = response.json()
print(f"New Access Token: {data.get('access_token')[:20]}...")
new_refresh_token = response.cookies.get('refresh_token')
print(f"New Refresh Token cookie set: {new_refresh_token is not None}")

# Test Logout
print("\nTesting Logout...")
response = client.post('/auth/logout')
print(f"Logout Status: {response.status_code}")

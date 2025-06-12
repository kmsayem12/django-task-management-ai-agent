# fmt: off
import os
import django

# Step 1: Set the settings module before any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
django.setup()

# Step 2: Now it's safe to import Django modules
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Step 3: Get or create token
username = input("Enter username: ").strip()


# Replace with actual username
try:
    user = User.objects.get(username=username)
    token, created = Token.objects.get_or_create(user=user)
    print(f"Token for user '{username}': {token.key}")
except User.DoesNotExist:
    print(f"User '{username}' does not exist.")

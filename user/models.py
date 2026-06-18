import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username          = None
    email             = models.EmailField(unique=True)

    name              = models.CharField(max_length=150, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    present_address   = models.TextField(blank=True, null=True)
    phone_number      = models.CharField(max_length=20, blank=True, null=True)
    image             = models.ImageField(upload_to='users/img', blank=True, null=True)
    is_online         = models.BooleanField(default=False)

    role = models.ForeignKey(
        'lookup.Lookup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        limit_choices_to={'name': 'role', 'is_active': True},
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []
    objects         = CustomUserManager()

    def __str__(self):
        return self.email

class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    refresh_token = models.CharField(max_length=512, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.user.email}"

class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.email}"

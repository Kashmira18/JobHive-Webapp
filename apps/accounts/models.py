from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES=(
        ('ADMIN','admin'),
        ('COMPANY','company'),
        ('CANDIDATE', 'candidate'),
    )

    role=models.CharField(max_length=20, choices=ROLE_CHOICES, default='CANDIDATE')
    # Required for company accounts for approved by admin
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username
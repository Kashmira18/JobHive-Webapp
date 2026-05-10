# from django.db import models
# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     ROLE_CHOICES=(
#         ('ADMIN','admin'),
#         ('COMPANY','company'),
#         ('CANDIDATE', 'candidate'),
#     )

#     role=models.CharField(max_length=20, choices=ROLE_CHOICES, default='CANDIDATE')
#     is_approved = models.BooleanField(default=False)

#     def __str__(self):
#         return self.username

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN','admin'),
        ("COMPANY", "Company"),
        ("CANDIDATE", "Candidate"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CANDIDATE")
    is_approved = models.BooleanField(default=False)  # sirf COMPANY ke liye
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

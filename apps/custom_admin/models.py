# from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminActivityLog(models.Model):
    """
    Admin actions ka log — optional but useful.
    """
    ACTION_CHOICES = [
        ("LOGIN",    "Login"),
        ("LOGOUT",   "Logout"),
        ("VIEW",     "View"),
        ("EDIT",     "Edit"),
        ("DELETE",   "Delete"),
    ]

    admin_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Admin Activity Log"

    def __str__(self):
        return f"{self.admin_user} — {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"

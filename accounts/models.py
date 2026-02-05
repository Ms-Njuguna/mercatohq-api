from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        SUPPORT = "SUPPORT", "Support"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SUPPORT,
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]

    def __str__(self):
        return f"{self.username} ({self.role})"

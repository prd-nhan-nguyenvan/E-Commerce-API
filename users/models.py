import os
import uuid

from django.conf import settings
from django.db import models


def upload_to(instance, filename):
    ext = filename.split(".")[-1]

    new_filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("profile_pictures", new_filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=upload_to, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.user}'s Profile"

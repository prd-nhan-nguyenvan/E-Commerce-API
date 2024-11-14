from django.dispatch import receiver

from .models import UserProfile
from .signals import create_new_user_signal


@receiver(create_new_user_signal)
def create_user_profile(sender, **kwargs):
    user = kwargs.get("user")
    UserProfile.objects.create(user=user)

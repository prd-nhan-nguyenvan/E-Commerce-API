from django.dispatch import receiver

from orders.signals import order_placed
from orders.tasks import send_ics


@receiver(order_placed)
def send_ics_email(sender, **kwargs):

    send_ics.delay(sender=sender, **kwargs)

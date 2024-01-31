from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now, timedelta

from apps.subscription.models import UserSubscription

@receiver(post_save, sender=UserSubscription)
def activate_subscription(sender, instance, created, **kwargs):
    if created and instance.payment_successful:
        instance.activate()

    if instance.expires_at < now():
        instance.deactivate()


from django.db.models import (
    CharField,
    ManyToManyField,
    ForeignKey,
    CASCADE,
    DecimalField,
    IntegerField,
    BooleanField,
    DateTimeField,
)
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta

from model_utils.models import TimeStampedModel


class UserSubscription(TimeStampedModel):
    """
    Represents a user's subscription to a specific tier.
    """
    user_id = IntegerField(null=True)
    group_id = IntegerField(null=True, unique=True)
    active = BooleanField(default=False)
    subscribed_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField(blank=True, null=True)
    transaction_id = CharField(max_length=255, blank=True, null=True)
    payment_successful = BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Subscription to {self.tier.name}"

    def activate(self):
        """
        Activates the subscription if payment was successful.
        """
        if self.payment_successful and self.transaction_id is not (None or ''):
            self.active = True
            self.expires_at = now() + timedelta(days=30)
            self.save(update_fields=['active', 'expires_at'])

            self.user.subscribed = True
            self.user.save(update_fields=['subscribed'])
            return True
        else:
            return False

    def deactivate(self):
        """
        Deactivates the subscription.
        """
        self.active = False
        self.expires_at = None
        self.save()

        self.user.subscribed = False
        self.user.save(update_fields=['subscribed'])


    class Meta:
        verbose_name = _("User Subscription")
        verbose_name_plural = _("User Subscriptions")
        ordering = ["-created"]

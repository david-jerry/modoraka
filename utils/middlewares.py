from apps.subscription.models import UserSubscription
from .mails import CustomEmailSender
from django.utils import timezone

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            # Check user's subscription status
            subscription = UserSubscription.objects.filter(user=user, active=True).first()

            if subscription and subscription.expires_at:
                # Deactivate subscription if it has expired
                if subscription.expires_at < timezone.now():
                    subscription.deactivate()

                    # Optionally, you can customize the response when subscription is deactivated
                    request.subscribed = False
                else:
                    request.subscribed = True

        response = self.get_response(request)
        return response

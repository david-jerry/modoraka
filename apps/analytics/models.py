from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone

from apps.subscription.models import UserSubscription

User = get_user_model()


class AnalysisData(models.Model):
    month = models.DateField(unique=True)
    total_subscriptions = models.IntegerField(default=0)
    daily_logged_in_users = models.IntegerField(default=0)
    new_registrations = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    @classmethod
    def update_analysis_data(cls):
        """
        ANALYSIS DATA FOR THE APPLICATION
        ------------------------------------------------------------------------
        Update the AnalysisData model with the latest aggregated data.

        USAGE:
            AnalysisData.update_analysis_data()

        NOTE:
            Can be used in signals or ran periodically using celery or crontab
        """
        # Calculate the start and end dates for the current month
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1, microsecond=0)

        # Calculate the start and end dates for the current day
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timezone.timedelta(days=1)

        # Get total subscriptions for the current month
        total_subscriptions = (
            UserSubscription.objects
            .filter(subscribed_at__range=(start_of_month, end_of_month))
            .count()
        )

        # Get total revenue for the current month
        total_revenue = (
            UserSubscription.objects
            .filter(subscribed_at__range=(start_of_month, end_of_month), payment_successful=True)
            .aggregate(models.Sum('tier__price'))['tier__price__sum'] or 0.0
        )

        # Get daily logged-in users for the current day
        daily_logged_in_users = (
            User.objects
            .filter(last_login__range=(start_of_day, end_of_day))
            .count()
        )

        # Get new registrations for the current month
        new_registrations = (
            User.objects
            .filter(date_joined__range=(start_of_month, end_of_month))
            .count()
        )

        # Update or create the AnalysisData instance
        analysis_data, created = cls.objects.get_or_create(month=start_of_month)
        analysis_data.total_subscriptions = total_subscriptions
        analysis_data.total_revenue = total_revenue
        analysis_data.daily_logged_in_users = daily_logged_in_users
        analysis_data.new_registrations = new_registrations
        analysis_data.save()

    def __str__(self):
        return f"Analysis Data for {self.month.strftime('%Y-%m')}"

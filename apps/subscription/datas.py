import os
import django

from asgiref.sync import sync_to_async

from utils.web3 import Web3Functions

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()


from apps.subscription.models import UserSubscription



@sync_to_async
def get_user_subscriptions(user_id):
    subs = []
    model_data = UserSubscription.objects.filter(user_id=user_id, active=True)
    for mod in model_data:
        subs.append({
            "user_id": mod.user_id,
            "group_id": mod.group_id,
            "active": mod.active,
            "subscribed_at": mod.subscribed_at,
            "expires_at": mod.expires_at,
            "transaction_id": mod.transaction_id,
            "payment_successful": mod.payment_successful,
        })
    return subs


@sync_to_async
def create_subscription(group_id, user_id, tx_id):
    subs = []
    successful = Web3Functions.check_transaction_success(Web3Functions, tx_id)
    data = {
        "user_id": user_id,
        "group_id": group_id,
        "payment_successful": successful,
        "transaction_id": tx_id,
    }
    UserSubscription.objects.create(**data)
    model_data = UserSubscription.objects.filter(user_id=user_id)
    for mod in model_data:
        subs.append({
            "user_id": mod.user_id,
            "group_id": mod.group_id,
            "active": mod.active,
            "subscribed_at": mod.subscribed_at,
            "expires_at": mod.expires_at,
            "transaction_id": mod.transaction_id,
            "payment_successful": mod.payment_successful,
        })
    return subs


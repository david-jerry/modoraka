import os
import django
from utils.web3 import Web3Functions

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from utils.logger import LOGGER

from django.utils.timezone import datetime, timedelta
from asgiref.sync import sync_to_async

from .models import (
    GroupOffenders,
    GroupPinnedMessages,
    TelegramGroup,
    TelegramGroupCaptcha,
    TelegramGroupFlooding,
    TelegramGroupMediaActions,
    User,
)
from apps.tokens.models import Tokens
from apps.subscription.models import UserSubscription


@sync_to_async
def get_users():
    users_dict = []
    users = User.objects.all()
    for user in users:
        users_dict.append(
            {
                "name": user.name,
                "chat_id": user.chat_id,
                "username": user.username,
                "user_id": user.user_id,
                "subscribed": user.subscribed,
                "violated": user.violated,
                "chosen_language": user.chosen_language,
                "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
            }
        )
    return users_dict


@sync_to_async
def get_user_by_username(username):
    try:
        LOGGER.debug(username)
        user = User.objects.get(username=username)
        user_dict = {
            "name": user.name,
            "username": user.username,
            "chat_id": user.chat_id,
            "user_id": user.user_id,
            "subscribed": user.subscribed,
            "violated": user.violated,
            "chosen_language": user.chosen_language,
            "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
        }
        return user_dict
    except User.DoesNotExist:
        return None
    except Exception as ex:
        LOGGER.error(str(ex))
        return None


@sync_to_async
def get_user(user_id):
    try:
        LOGGER.debug(user_id)
        user = User.objects.get(user_id=user_id)
        user_dict = {
            "name": user.name,
            "username": user.username,
            "chat_id": user.chat_id,
            "user_id": user.user_id,
            "subscribed": user.subscribed,
            "violated": user.violated,
            "chosen_language": user.chosen_language,
            "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
        }
        return user_dict
    except User.DoesNotExist:
        return None
    except Exception as ex:
        LOGGER.error(str(ex))
        return None


@sync_to_async
def create_user(data):
    User.objects.get_or_create(
        user_id=data["user_id"],
        defaults={
            "name": data["name"],
            "chat_id": data["chat_id"],
            "username": data["username"],
            "user_id": data["user_id"],
            "subscribed": data["subscribed"],
            "violated": data["violated"],
            "chosen_language": data["chosen_language"],
        },
    )
    user = User.objects.get(user_id=data["user_id"])
    user_dict = {
        "name": user.name,
        "chat_id": user.chat_id,
        "username": user.username,
        "user_id": user.user_id,
        "subscribed": user.subscribed,
        "violated": user.violated,
        "chosen_language": user.chosen_language,
        "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
    }
    return user_dict


@sync_to_async
def update_user(user_id, data):
    user = User.objects.get(user_id=user_id)

    # Update user_data fields based on updated_data dictionary
    for key, value in data.items():
        setattr(user, key, value)

    user.save()
    group_dict = {
        "name": user.name,
        "chat_id": user.chat_id,
        "username": user.username,
        "user_id": user.user_id,
        "subscribed": user.subscribed,
        "violated": user.violated,
        "chosen_language": user.chosen_language,
        "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
    }
    return group_dict


@sync_to_async
def update_user_group(user_id, group_id):
    try:
        user = User.objects.get(user_id=user_id)
        group = TelegramGroup.objects.get(chat_id=group_id)
        user.groups.add(group)
        # user.save(update_fields=["groups"])
        user_dict = {
            "name": user.name,
            "chat_id": user.chat_id,
            "username": user.username,
            "user_id": user.user_id,
            "subscribed": user.subscribed,
            "violated": user.violated,
            "chosen_language": user.chosen_language,
            "groups": [{"chat_id": group.chat_id, "name": group.group_name} for group in user.groups.all()],
        }
        return user_dict
    except User.DoesNotExist:
        return None




@sync_to_async
def get_groups(user_id):
    groups_dict = []
    user = User.objects.get(user_id=user_id)
    for group in user.groups.all():
        group_dict = {
            "chat_id": group.chat_id,
            "group_name": group.group_name,
            "about": group.about,
            "welcome_message": group.welcome_message,
            "goodbye_message": group.goodbye_message,
            "max_warnings": group.max_warnings,
            "mute_duration": group.mute_duration,
            "ban_duration": group.ban_duration,
            "max_message_length": group.max_message_length,
            "website": group.website,
            "support": group.support,
            "but_token_link": group.but_token_link,
            "buy_token_name": {
                "token_symbol": group.buy_token_name.ticker_symbol,
                "token_id": group.buy_token_name.ticker_id,
                "token_name": group.buy_token_name.ticker_name,
                "token_total_supply": group.buy_token_name.total_supply,
                "token_circulating_supply": group.buy_token_name.circulating_supply,
                "token_usd_price": group.buy_token_name.usd_price,
                "token_address": group.buy_token_name.token_address,
                "token_abi": group.buy_token_name.token_abi,
                "token_router_address": group.buy_token_name.token_router_address,
                "token_router_abi": group.buy_token_name.token_router_abi,
            }
            if group.buy_token_name
            else None,
            "allow_links": group.allow_links,
            "must_have_username": group.must_have_username,
            "block_porn": group.block_porn,
            "watch_for_spam": group.watch_for_spam,
            "enable_captcha": group.enable_captcha,
            "unverified_user_duration": group.unverified_user_duration,
            "watch_length": group.watch_length,
            "allow_hash": group.allow_hash,
            "prevent_flooding": group.prevent_flooding,
            "delete_messages": group.delete_messages,
            "subscribed": group.subscribed,
            "offenders": [off for off in group.offenders],
        }
        groups_dict.append(group_dict)
    return groups_dict


@sync_to_async
def get_group(chat_id):
    try:
        group = TelegramGroup.objects.get(chat_id=chat_id)
        group_dict = {
            "chat_id": group.chat_id,
            "group_name": group.group_name,
            "about": group.about,
            "welcome_message": group.welcome_message,
            "goodbye_message": group.goodbye_message,
            "max_warnings": group.max_warnings,
            "mute_duration": group.mute_duration,
            "ban_duration": group.ban_duration,
            "max_message_length": group.max_message_length,
            "website": group.website,
            "support": group.support,
            "but_token_link": group.but_token_link,
            "buy_token_name": {
                "token_symbol": group.buy_token_name.ticker_symbol,
                "token_id": group.buy_token_name.ticker_id,
                "token_name": group.buy_token_name.ticker_name,
                "token_total_supply": group.buy_token_name.total_supply,
                "token_circulating_supply": group.buy_token_name.circulating_supply,
                "token_usd_price": group.buy_token_name.usd_price,
                "token_address": group.buy_token_name.token_address,
                "token_abi": group.buy_token_name.token_abi,
                "token_router_address": group.buy_token_name.token_router_address,
                "token_router_abi": group.buy_token_name.token_router_abi,
            }
            if group.buy_token_name
            else None,
            "allow_links": group.allow_links,
            "must_have_username": group.must_have_username,
            "block_porn": group.block_porn,
            "unverified_user_duration": group.unverified_user_duration,
            "watch_for_spam": group.watch_for_spam,
            "enable_captcha": group.enable_captcha,
            "watch_length": group.watch_length,
            "allow_hash": group.allow_hash,
            "prevent_flooding": group.prevent_flooding,
            "subscribed": group.subscribed,
            "delete_messages": group.delete_messages,
            "offenders": [off for off in group.offenders],
        }
        return group_dict
    except TelegramGroup.DoesNotExist:
        return None
    except Exception as ex:
        LOGGER.error(str(ex))
        return None


@sync_to_async
def create_group(data):
    try:
        LOGGER.info("User doesn't exist")
        TelegramGroup.objects.get_or_create(
            chat_id=data["chat_id"],
            defaults={
                "chat_id": data["chat_id"],
                "group_name": data["group_name"],
                "about": data["about"],
            },
        )
        group = TelegramGroup.objects.get(chat_id=data["chat_id"])
        group_dict = {
            "chat_id": group.chat_id,
            "group_name": group.group_name,
            "about": group.about,
            "welcome_message": group.welcome_message,
            "goodbye_message": group.goodbye_message,
            "max_warnings": group.max_warnings,
            "mute_duration": group.mute_duration,
            "ban_duration": group.ban_duration,
            "max_message_length": group.max_message_length,
            "website": group.website,
            "support": group.support,
            "but_token_link": group.but_token_link,
            "buy_token_name": {
                "token_symbol": group.buy_token_name.ticker_symbol,
                "token_id": group.buy_token_name.ticker_id,
                "token_name": group.buy_token_name.ticker_name,
                "token_total_supply": group.buy_token_name.total_supply,
                "token_circulating_supply": group.buy_token_name.circulating_supply,
                "token_usd_price": group.buy_token_name.usd_price,
                "token_address": group.buy_token_name.token_address,
                "token_abi": group.buy_token_name.token_abi,
                "token_router_address": group.buy_token_name.token_router_address,
                "token_router_abi": group.buy_token_name.token_router_abi,
            }
            if group.buy_token_name
            else None,
            "allow_links": group.allow_links,
            "must_have_username": group.must_have_username,
            "block_porn": group.block_porn,
            "allow_hash": group.allow_hash,
            "unverified_user_duration": group.unverified_user_duration,
            "enable_captcha": group.enable_captcha,
            "watch_for_spam": group.watch_for_spam,
            "watch_length": group.watch_length,
            "prevent_flooding": group.prevent_flooding,
            "subscribed": group.subscribed,
            "delete_messages": group.delete_messages,
            "offenders": [off for off in group.offenders],
        }
        return group_dict
    except TelegramGroup.DoesNotExist:
        return None
    except Exception as e:
        LOGGER.info(str(e))
        return None


@sync_to_async
def update_group(chat_id, data):
    try:
        group = TelegramGroup.objects.get(chat_id=chat_id)

        # Update user_data fields based on updated_data dictionary
        for key, value in data.items():
            setattr(group, key, value)

        group.save()
        group_dict = {
            "chat_id": group.chat_id,
            "group_name": group.group_name,
            "about": group.about,
            "welcome_message": group.welcome_message,
            "goodbye_message": group.goodbye_message,
            "max_warnings": group.max_warnings,
            "mute_duration": group.mute_duration,
            "ban_duration": group.ban_duration,
            "max_message_length": group.max_message_length,
            "website": group.website,
            "support": group.support,
            "but_token_link": group.but_token_link,
            "buy_token_name": {
                "token_symbol": group.buy_token_name.ticker_symbol,
                "token_id": group.buy_token_name.ticker_id,
                "token_name": group.buy_token_name.ticker_name,
                "token_total_supply": group.buy_token_name.total_supply,
                "token_circulating_supply": group.buy_token_name.circulating_supply,
                "token_usd_price": group.buy_token_name.usd_price,
                "token_address": group.buy_token_name.token_address,
                "token_abi": group.buy_token_name.token_abi,
                "token_router_address": group.buy_token_name.token_router_address,
                "token_router_abi": group.buy_token_name.token_router_abi,
            }
            if group.buy_token_name
            else None,
            "allow_links": group.allow_links,
            "must_have_username": group.must_have_username,
            "block_porn": group.block_porn,
            "watch_for_spam": group.watch_for_spam,
            "unverified_user_duration": group.unverified_user_duration,
            "watch_length": group.watch_length,
            "enable_captcha": group.enable_captcha,
            "allow_hash": group.allow_hash,
            "prevent_flooding": group.prevent_flooding,
            "subscribed": group.subscribed,
            "delete_messages": group.delete_messages,
            "offenders": [off for off in group.offenders],
        }
        return group_dict
    except TelegramGroup.DoesNotExist:
        return None


@sync_to_async
def update_group_watch_token(chat_id, token_symbol):
    try:
        token = Tokens.objects.get(ticker_symbol=token_symbol.upper())
        group = TelegramGroup.objects.get(chat_id=chat_id)
        group.buy_token_name = token
        group.save(update_fields=["buy_token_name"])
        group_dict = {
            "chat_id": group.chat_id,
            "group_name": group.group_name,
            "about": group.about,
            "welcome_message": group.welcome_message,
            "goodbye_message": group.goodbye_message,
            "max_warnings": group.max_warnings,
            "mute_duration": group.mute_duration,
            "max_message_length": group.max_message_length,
            "ban_duration": group.ban_duration,
            "website": group.website,
            "support": group.support,
            "but_token_link": group.but_token_link,
            "buy_token_name": {
                "token_symbol": group.buy_token_name.ticker_symbol,
                "token_id": group.buy_token_name.ticker_id,
                "token_name": group.buy_token_name.ticker_name,
                "token_total_supply": group.buy_token_name.total_supply,
                "token_circulating_supply": group.buy_token_name.circulating_supply,
                "token_usd_price": group.buy_token_name.usd_price,
                "token_address": group.buy_token_name.token_address,
                "token_abi": group.buy_token_name.token_abi,
                "token_router_address": group.buy_token_name.token_router_address,
                "token_router_abi": group.buy_token_name.token_router_abi,
            }
            if group.buy_token_name
            else None,
            "allow_links": group.allow_links,
            "must_have_username": group.must_have_username,
            "block_porn": group.block_porn,
            "enable_captcha": group.enable_captcha,
            "allow_hash": group.allow_hash,
            "unverified_user_duration": group.unverified_user_duration,
            "watch_for_spam": group.watch_for_spam,
            "watch_length": group.watch_length,
            "prevent_flooding": group.prevent_flooding,
            "subscribed": group.subscribed,
            "delete_messages": group.delete_messages,
            "offenders": [off for off in group.offenders],
        }
        return group_dict
    except Tokens.DoesNotExist:
        return None


@sync_to_async
def reset_group_offenders(chat_id, user_id):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    offender = GroupOffenders.objects.get(group=group, user_id=user_id)

    offender.warned_times = group.ban_duration
    offender.start_date = None
    offender.end_date = None

    offender.save()
    group.offender.pop(user_id)

    action_dict = {
        "group": {"chat_id": offender.group.chat_id, "group_name": offender.group.group_name},
        "user_id": offender.user_id,
        "warned_times": offender.warned_times,
        "start_date": offender.start_date,
        "end_date": offender.end_date,
    }
    return action_dict


@sync_to_async
def add_group_offenders(chat_id, user_id):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    GroupOffenders.objects.get_or_create(group=group, defaults={"group": group, "user_id": user_id})
    offender = GroupOffenders.objects.get(group=group)
    LOGGER.info(f"Number of warning left: {offender.warned_times}")
    if offender.warned_times > 0:
        offender.warned_times -= 1
        offender.save(update_fields=["warned_times"])
    elif offender.warned_times == 0:
        offender.start_date = datetime.now()
        offender.end_date = datetime.now() + timedelta(days=group.ban_duration)
        offender.save(update_fields=["start_date", "end_date"])
        group.offenders.append(user_id)
        # group.save(update_fields=['offenders'])

    group_dict = {
        "chat_id": group.chat_id,
        "group_name": group.group_name,
        "about": group.about,
        "welcome_message": group.welcome_message,
        "goodbye_message": group.goodbye_message,
        "max_warnings": group.max_warnings,
        "mute_duration": group.mute_duration,
        "ban_duration": group.ban_duration,
        "max_message_length": group.max_message_length,
        "website": group.website,
        "support": group.support,
        "but_token_link": group.but_token_link,
        "buy_token_name": {
            "token_symbol": group.buy_token_name.ticker_symbol,
            "token_id": group.buy_token_name.ticker_id,
            "token_name": group.buy_token_name.ticker_name,
            "token_total_supply": group.buy_token_name.total_supply,
            "token_circulating_supply": group.buy_token_name.circulating_supply,
            "token_usd_price": group.buy_token_name.usd_price,
            "token_address": group.buy_token_name.token_address,
            "token_abi": group.buy_token_name.token_abi,
            "token_router_address": group.buy_token_name.token_router_address,
            "token_router_abi": group.buy_token_name.token_router_abi,
        }
        if group.buy_token_name
        else None,
        "allow_links": group.allow_links,
        "must_have_username": group.must_have_username,
        "block_porn": group.block_porn,
        "enable_captcha": group.enable_captcha,
        "allow_hash": group.allow_hash,
        "watch_for_spam": group.watch_for_spam,
        "watch_length": group.watch_length,
        "unverified_user_duration": group.unverified_user_duration,
        "subscribed": group.subscribed,
        "prevent_flooding": group.prevent_flooding,
        "delete_messages": group.delete_messages,
        "offenders": [off for off in group.offenders],
    }
    return group_dict


@sync_to_async
def add_media_actions(chat_id):
    try:
        group = TelegramGroup.objects.get(chat_id=chat_id)
        TelegramGroupMediaActions.objects.get_or_create(group=group, defaults={"group": group})
        media_actions = TelegramGroupMediaActions.objects.get(group=group)
        action_dict = {
            "group": {"chat_id": media_actions.group.chat_id, "group_name": media_actions.group.group_name},
            "images": media_actions.images,
            "videos": media_actions.videos,
            "animation": media_actions.animation,
            "audio": media_actions.audio,
            "sticker": media_actions.sticker,
            "documents": media_actions.documents,
        }
        return action_dict
    except Exception as e:
        LOGGER.info(f"Media Error: {str(e)}")
        return None


@sync_to_async
def update_media_actions(chat_id, data):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    media_actions = TelegramGroupMediaActions.objects.get(group=group)

    for key, value in data.items():
        setattr(media_actions, key, value)

    media_actions.save()

    action_dict = {
        "group": {"chat_id": media_actions.group.chat_id, "group_name": media_actions.group.group_name},
        "images": media_actions.images,
        "videos": media_actions.videos,
        "animation": media_actions.animation,
        "audio": media_actions.audio,
        "sticker": media_actions.sticker,
        "documents": media_actions.documents,
    }
    return action_dict


@sync_to_async
def add_flood_settings(chat_id):
    try:
        group = TelegramGroup.objects.get(chat_id=chat_id)
        TelegramGroupFlooding.objects.get_or_create(group=group, defaults={"group": group})
        media_actions = TelegramGroupFlooding.objects.get(group=group)
        action_dict = {
            "group": {
                "chat_id": media_actions.group.chat_id,
                "subscribed": media_actions.group.subscribed,
                "group_name": media_actions.group.group_name,
            },
            "messages_before_block": media_actions.messages_before_block,
            "repeats_timeframe": media_actions.repeats_timeframe,
            "ban": media_actions.ban,
            "kick": media_actions.kick,
            "mute": media_actions.mute,
        }
        return action_dict
    except Exception as e:
        LOGGER.info(f"Flood Settings Error: {str(e)}")
        return None


@sync_to_async
def update_flood_settings(chat_id, data):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    media_actions = TelegramGroupFlooding.objects.get(group=group)

    for key, value in data.items():
        setattr(media_actions, key, value)

    media_actions.save()

    action_dict = {
        "group": {
            "chat_id": media_actions.group.chat_id,
            "subscribed": media_actions.group.subscribed,
            "group_name": media_actions.group.group_name,
        },
        "messages_before_block": media_actions.messages_before_block,
        "repeats_timeframe": media_actions.repeats_timeframe,
        "ban": media_actions.ban,
        "kick": media_actions.kick,
        "mute": media_actions.mute,
    }
    return action_dict


@sync_to_async
def create_captcah(chat_id, user_id, captcha_code):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    timestamp = datetime.now() + timedelta(days=group.unverified_user_duration)
    data = {"group": group, "user_id": user_id, "captcha_code": captcha_code, "expires": timestamp, "used": False}
    TelegramGroupCaptcha.objects.update_or_create(group=group, defaults=data)
    return data


@sync_to_async
def get_captcah(chat_id, user_id):
    try:
        group = TelegramGroup.objects.get(chat_id=chat_id)
        captcha = TelegramGroupCaptcha.objects.get(group=group, user_id=user_id)
        data = {
            "group": captcha.group.chat_id,
            "user_id": captcha.user_id,
            "captcha_code": captcha.captcha_code,
            "expires": captcha.expires,
            "used": captcha.used,
        }
        return data
    except Exception as e:
        LOGGER.info(e)
        return None


@sync_to_async
def verify_captcah(chat_id, user_id, captcha_code):
    captcha = TelegramGroupCaptcha.objects.get(user_id=user_id, captcha_code=captcha_code)

    if datetime.now() > captcha.expires:
        captcha.delete()
        return create_captcah(chat_id, user_id, captcha_code)
    else:
        captcha.used = True
        captcha.save(update_fields=["used"])

    data = {
        "group": captcha.group,
        "user_id": captcha.user_id,
        "captcha_code": captcha.captcha_code,
        "expires": captcha.expires,
        "used": captcha.used,
    }
    return data


@sync_to_async
def add_group_pinned_messages(chat_id, message_id, message_text):
    group = TelegramGroup.objects.get(chat_id=chat_id)
    GroupPinnedMessages.objects.get_or_create(
        pinned_message_id=message_id,
        defaults={
            "group": group,
            "pinned_message_id": message_id,
            "pinned_message_text": message_text,
        },
    )
    pinned = GroupPinnedMessages.objects.get(pinned_message_id=message_id)
    pinned_dict = {
        "group": pinned.group.chat_id,
        "pinned_message_id": pinned.pinned_message_id,
        "pinned_message_chat": pinned.pinned_message_chat,
    }
    return pinned_dict


@sync_to_async
def get_all_pinned_messages(chat_id):
    pins = []
    group = TelegramGroup.objects.get(chat_id=chat_id)
    pins_data = GroupPinnedMessages.objects.filter(group=group)
    for pinned in pins_data:
        p_dict = {
            "group": pinned.group.chat_id,
            "pinned_message_id": pinned.pinned_message_id,
            "pinned_message_chat": pinned.pinned_message_chat,
        }
        pins.append(p_dict)
    return pins


@sync_to_async
def remove_pin(chat_id, message_id):
    pin = GroupPinnedMessages.objects.get(pinned_message_id=message_id)
    pin.delete()
    return get_all_pinned_messages(chat_id)



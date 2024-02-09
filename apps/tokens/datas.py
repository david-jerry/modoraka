import os
import django

from asgiref.sync import sync_to_async

from apps.users.models import TelegramGroup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.tokens.models import Tokens, WatchToken, WatchAddress


@sync_to_async
def get_tokens():
    user = Tokens.objects.all()
    user_dict = user.values()
    return user_dict


@sync_to_async
def get_token(symbol):
    user = Tokens.objects.get(ticker_symbol=symbol.upper())
    user_dict = user.__dict__
    return user_dict




@sync_to_async
def get_tokens_watched():
    tokens_dict = []
    tokens = WatchToken.objects.all()
    for watched in tokens:
        t_dict = {
            'groups': watched.groups,
            'token': {
                "token_symbol": watched.token.ticker_symbol,
                "token_name": watched.token.ticker_name,
                "total_supply": watched.token.total_supply,
                "token_circulating_supply": watched.token.circulating_supply,
                "token_usd_price": watched.token.usd_price,
                "token_address": watched.token.token_address,
                "token_abi": watched.token.token_abi,
                "token_router_address": watched.token.token_router_address,
                "token_router_abi": watched.token.token_router_abi,
            }
        }
        tokens_dict.append(t_dict)
    return tokens_dict

@sync_to_async
def create_tokens_watched(chat_id, ticker_symbol):
    token = Tokens.objects.get(ticker_symbol=ticker_symbol)
    WatchToken.objects.get_or_create(token=token)
    watched = WatchToken.objects.get(token=token)
    if not WatchToken.objects.filter(groups__in=[chat_id]).exists():
        watched.groups += f"{chat_id}, "
        watched.save(update_fields=['groups'])
    tokens_dict = {
        'groups': watched.groups,
        'token': {
            "token_symbol": watched.token.ticker_symbol,
            "token_name": watched.token.ticker_name,
            "total_supply": watched.token.total_supply,
            "token_circulating_supply": watched.token.circulating_supply,
            "token_usd_price": watched.token.usd_price,
            "token_address": watched.token.token_address,
            "token_abi": watched.token.token_abi,
            "token_router_address": watched.token.token_router_address,
            "token_router_abi": watched.token.token_router_abi,
        }
    }
    return tokens_dict

@sync_to_async
def get_token_watched(chat_id):
    if WatchToken.objects.filter(groups__in=[chat_id]).exists():
        watched = WatchToken.objects.filter(groups__in=[chat_id]).first()
        tokens_dict = {
            'groups': watched.groups,
            'token': {
                "token_symbol": watched.token.ticker_symbol,
                "token_name": watched.token.ticker_name,
                "total_supply": watched.token.total_supply,
                "token_circulating_supply": watched.token.circulating_supply,
                "token_usd_price": watched.token.usd_price,
                "token_address": watched.token.token_address,
                "token_abi": watched.token.token_abi,
                "token_router_address": watched.token.token_router_address,
                "token_router_abi": watched.token.token_router_abi,
            }
        }
        return tokens_dict
    return None

@sync_to_async
def get_tokens_watched_by_group(chat_id):
    tokens_dict = []
    tokens = WatchToken.objects.filter(groups__in=[chat_id])
    for watched in tokens:
        t_dict = {
            'groups': watched.groups,
            'token': {
                "token_symbol": watched.token.ticker_symbol,
                "token_name": watched.token.ticker_name,
                "total_supply": watched.token.total_supply,
                "token_circulating_supply": watched.token.circulating_supply,
                "token_usd_price": watched.token.usd_price,
                "token_address": watched.token.token_address,
                "token_abi": watched.token.token_abi,
                "token_router_address": watched.token.token_router_address,
                "token_router_abi": watched.token.token_router_abi,
            }
        }
        tokens_dict.append(t_dict)
    return tokens_dict






# @sync_to_async
# def get_addresses_watched():
#     violators = WatchAddress.objects.all()
#     violators_dict = violators.values()
#     return violators_dict

# @sync_to_async
# def get_addresses_watched_by_user(chat_id):
#     user = User.objects.get(chat_id=chat_id)
#     violators = WatchAddress.objects.filter(user__in=user)
#     violators_dict = violators_dict.values()
#     return violators_dict

# @sync_to_async
# def create_addresses_watched(chat_id, address):
#     user = User.objects.get(chat_id=chat_id)
#     violators = WatchAddress.objects.get_or_create(address=address)
#     violators.users.add(user)
#     violators.save(update_fields=['users'])
#     violators_dict = violators_dict.__dict__
#     return violators_dict

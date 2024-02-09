import re
import os
import django

from apps.users.datas import get_exception_links, reset_group_offenders

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from pprint import pprint
from telegram import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    MessageEntity,
    ChatPermissions,
    ChatAdministratorRights,
)
from django.utils.timezone import datetime, timedelta
from telegram.constants import ParseMode, ChatAction
from apps.users.models import TelegramGroup, User
from commands.start.buttons import generate_button

from utils.env_result import INFURA_HTTP_URL
from utils.logger import LOGGER

from utils.constants import (
    about_message,
)

today = datetime.now()

with open("apps/static/images/profile_photo.gif", "rb") as file:
    LOGGER.debug(file)
    bot_static_profile_photo = file.read()


def get_message_stack(context):
    if not context.user_data.get("message_stack"):
        context.user_data["message_stack"] = []
    return context.user_data.get("message_stack")


# filter checks
class GroupBotFilters:
    def __init__(self):
        pass

    async def bot_usernames_exist_filter(self, message, chat_id) -> bool:
        bot_username_regex = r"@\w+(bot|Bot|_bot|_Bot)"  # Adjust regex if needed
        word_exceptions = await get_exception_links(chat_id)

        try:
            return any(
                re.match(bot_username_regex, username)
                for entity in message.entities
                if not username in word_exceptions and (entity.type == MessageEntity.MENTION or entity.type == MessageEntity.TEXT_MENTION)
                for username in message.text[entity.offset : entity.offset + entity.length]
            )
        except Exception as e:
            LOGGER.debug(str(e))
            return bool(re.search(bot_username_regex, message.text))

    async def links_exist_filter(self, message, chat_id) -> bool:
        link_regex = r"\b(\S+(?:\.com|\.org|\.\w+))\b"  # Match HTTP/HTTPS links and bare URLs
        link_exceptions = await get_exception_links(chat_id)

        try:
            links_in_message = re.findall(link_regex, message.text)

            # Check if any of the links are exceptions
            link_exceptions = await get_exception_links(chat_id)
            if any(not link in link_exceptions for link in links_in_message):
                return True  # Check for links using regex
            return False
        except Exception as e:
            LOGGER.debug(str(e))  # Log exception if regex fails

        # If regex fails or raises an exception, fall back to entity check
        return any(entity.type == MessageEntity.TEXT_LINK for entity in message.entities)


# return messages
async def return_message(
    bot,
    chat_id: str | int,
    message: str,
    message_stack: list,
    message_id: str | int = None,
    new_markup: bool = False,
    back_exists: bool = False,
    input_placeholder: str = None,
    markup=[],
):
    if back_exists:
        markup.append(InlineKeyboardButton("⬅ Back", callback_data="back"))

    # Prepare message content
    message_content = {"chat_id": chat_id, "message": message, "markup": markup, "message_id": message_id}

    # Push new message content to the stack
    message_stack.append(message_content)

    # Create keyboard from markup
    keyboard = InlineKeyboardMarkup(markup)

    # Send message with optional photo
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    if input_placeholder is not None:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            reply_markup=ForceReply(selective=True, input_field_placeholder=input_placeholder),
        )
    elif new_markup:
        await bot.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, text=message, parse_mode=ParseMode.HTML, reply_markup=keyboard
        )
    elif message_id is not None and new_markup:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=message, parse_mode=ParseMode.HTML, reply_markup=keyboard
        )
    else:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, reply_markup=keyboard)


class BotInformation:
    def __init__(self):
        pass

    async def get_about_text(self, bot) -> str:
        bot_info = await bot.get_me()
        LOGGER.debug(bot_info)
        return about_message

    async def get_bot_photo(self, bot):
        try:
            bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
            bot_profile_photo = bot_profile_photos.photos[0][0]
            return bot_profile_photo
        except Exception as e:
            LOGGER.info(str(e))
            return bot_static_profile_photo

    async def get_bot_discription_photo(self, bot, bot_username):
        try:
            bot_profile_photo = await bot.get_profile_photo(bot_username)
            return bot_profile_photo
        except Exception as e:
            LOGGER.info(str(e))
            return bot_static_profile_photo


class GroupBotActions:
    def __init__(self):
        pass

    async def get_members_count(self, bot, chat_id) -> int:
        count = await bot.get_chat_member_count(chat_id=chat_id)
        return count

    async def get_all_administrators(self, chat_id, bot) -> list:
        admins = await bot.get_chat_administrators(chat_id=chat_id)
        return admins

    async def get_group_member(self, chat_id, user_id, bot):
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member

    async def get_group_name(self, bot, chat_id) -> str:
        name = await bot.get_chat(chat_id=chat_id)
        LOGGER.info(f"Group Name: {name.title}")
        return name.title

    async def get_group_about(self, bot, chat_id) -> str:
        name = await bot.get_chat(chat_id=chat_id)
        LOGGER.info(f"Group Name: {name.description}")
        return name.description

    async def exit_group(self, bot, chat_id):
        await bot.leave_chat(chat_id=chat_id)

    async def create_group_invite_link(
        self,
        bot,
        chat_id,
        group_name: str,
        invite_link_expires_in: int = 10,
        member_limit: int = 50,
        create_join_request: bool = True,
    ):
        ban_date = today + timedelta(days=invite_link_expires_in)
        await bot.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=ban_date,
            member_limit=member_limit,
            name=group_name,
            creates_join_request=create_join_request,
        )

    async def approve_group_join_request(self, chat_id, user_id, bot) -> None:
        await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

    async def pin_message(self, chat_id, message_id, bot) -> None:
        await bot.pin_chat_message(chat_id=chat_id, message_id=message_id, disable_notification=False)

    async def unpin_message(self, chat_id, message_id, bot) -> None:
        await bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)

    async def unpin_all_message(self, chat_id, bot) -> None:
        await bot.unpin_all_chat_message(chat_id=chat_id)

    async def ban_chat_member(self, chat_id, user_id, bot, ban_duration_in_days) -> None:
        LOGGER.info(ban_duration_in_days)
        ban_date = today + timedelta(days=ban_duration_in_days)
        LOGGER.info(ban_date)
        user = await self.get_group_member(self, chat_id, user_id, bot)
        LOGGER.info(pprint(user))
        await reset_group_offenders(chat_id, user_id)
        await self._send_typing_chat_action(self, chat_id, bot)
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=ban_date)
        await bot.send_message(chat_id=chat_id, text=f"You have been banned for offending the rules governing this group")

    async def restrict_chat_member(self, chat_id, user_id, bot, mute_duration_in_seconds) -> None:
        ban_date = today + timedelta(seconds=mute_duration_in_seconds)
        await reset_group_offenders(chat_id, user_id)
        await bot.restrict_chat_member(
            chat_id=chat_id, user_id=user_id, until_date=ban_date, permissions=ChatPermissions.NONE
        )


    async def _send_typing_chat_action(self, chat_id, bot) -> None:
        """Sends a chat action, handling potential deprecation of ChatAction."""
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        except AttributeError:
            pass

    async def promote_chat_member(self, bot, chat_id, user_id, role) -> None:
        permissions = self._get_permissions_for_role(role)
        await bot.promote_chat_member(chat_id=chat_id, user_id=user_id, **permissions)

    def _get_permissions_for_role(self, role: str) -> dict:
        role_permissions = {
            "SUPERADMIN": self._superadmin_permissions(),
            "MODERATOR": self._moderator_permissions(),
            "ENFORCER": self._enforcer_permissions(),
        }
        return role_permissions.get(role, {})

    def _superadmin_permissions(self) -> dict:
        return {
            "can_change_info": True,
            "can_post_messages": True,
            "can_edit_messages": True,
            "can_delete_messages": True,
            "can_invite_users": True,
            "can_restrict_members": True,
            "can_pin_messages": True,
            "can_promote_members": True,
            "is_anonymous": True,
            "can_manage_chat": True,
            "can_manage_video_chats": True,
            "can_manage_topics": True,
            "can_post_stories": True,
            "can_edit_stories": True,
            "can_delete_stories": True,
        }

    def _moderator_permissions(self) -> dict:
        permissions = self._superadmin_permissions().copy()
        permissions.pop("can_change_info", None)
        return permissions

    def _enforcer_permissions(self) -> dict:
        permissions = self._moderator_permissions().copy()
        permissions.pop("can_post_messages", None)
        return permissions


def validate_token_address(address: str) -> str:
    try:
        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(f"{INFURA_HTTP_URL}"))
        return w3.to_checksum_address(address)
    except Exception as e:
        LOGGER.error(str(e))
        return f"Error: {str(e)}"


# class TokenDetails:
#     def __init__(self, contract):
#         self.contract = contract

#     def get_token_fiat_price(self, symbol: str, fiat: str) -> float:
#         client = Client(api_key=COINBASE_API, api_secret=COINBASE_SK)
#         apereq = client.get_buy_price(currency_pair=f'{symbol.upper()}-{fiat.upper()}')
#         price = apereq['amount']
#         result=float(price)
#         return round(result, 2)

#     def get_token_eth_price(self, symbol: str) -> float:
#         apereq = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}ETH').json()
#         price = apereq['price']
#         result=float(price)
#         return round(result, 2)

#     def get_token_decimals(self) -> int:
#         decimal = self.contract.functions.decimal().call()
#         return decimal

#     def get_total_supply(self):
#         decimal = self.get_token_decimals()
#         total = self.contract.functions.totalSupply().call() / 10**9
#         res = float(total)
#         return round(res, 6)

#     def get_name(self) -> str:
#         return self.contract.functions.name().call()

#     def get_symbol(self) -> str:
#         return self.contract.functions.symbol().call()

#     def get_liquidity(self) -> int:
#         pair_address = self.contract.functions.pair().call()
#         if pair_address:
#             result = self.contract.functions.balanceOf(pair_address).call() * 2
#             return result
#         else:
#             return 0

#     def get_circulating_supply(self) -> int:
#         c_supply = self.contract.functions.getCirculatingSupply().call()
#         return c_supply

#     def get_marketcapital_in_usd(self, symbol: str) -> float:
#         client = CoinMetricsClient()
#         client.get

#     def get_burned_amount(self) -> int:
#         burned_address = self.contract.functions.burnFeeReceiver().call()
#         if burned_address:
#             result = self.contract.functions.balanceOf(burned_address).call()
#             return result
#         else:
#             return 0

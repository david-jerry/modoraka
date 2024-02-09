import os
from pprint import pprint
import re
import django

from apps.tokens.datas import create_tokens_watched, get_token_watched


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.utils.timezone import datetime, timedelta

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update, helpers
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    CallbackContext,
    ConversationHandler,
)
from telegram.constants import ParseMode, ChatAction, ChatMemberStatus
from commands.start.buttons import generate_button

from utils.constants import (
    help_message,
    about_message,
    language_message,
    home_message,
)
from utils.logger import LOGGER
from utils.utils import GroupBotActions, get_message_stack, return_message


from apps.users.datas import (
    create_captcah,
    create_group,
    create_user,
    get_banned_words,
    get_captcah,
    get_exception_links,
    get_flood_settings,
    get_group,
    get_groups,
    get_user,
    get_user_by_username,
    update_banned_words,
    update_exception_links,
    update_flood_settings,
    update_group,
    update_user,
    update_user_group,
    view_user_groups,
)

# from apps.subscription.datas import get_subscription_tier, get_subscription_tiers

home_button = InlineKeyboardButton("🏠 Home 🏠", callback_data="home")
add_button = InlineKeyboardButton("➕ Add Modoraka to Group ➕", url="https://t.me/modoraka_bot?startgroup=start")
trade_button = InlineKeyboardButton("🎯 Add TradoRaka to Group 🎯", url="https://t.me/modoraka_bot")


language_button = InlineKeyboardButton("🌐 Bot Language 🌐", callback_data="choose_language")
english_button = InlineKeyboardButton("🇬🇧  English 🇬🇧 ", callback_data="choose_english")
back_button = InlineKeyboardButton("↔ Back ", callback_data="back")
cancel_button = InlineKeyboardButton("✖ Cancel ", callback_data="cancel")
spanish_button = InlineKeyboardButton("🇪🇸 Spainish 🇪🇸", callback_data="choose_spanish")
french_button = InlineKeyboardButton("🇫🇷 French 🇫🇷", callback_data="choose_french")
italian_button = InlineKeyboardButton("🇮🇹 Italian 🇮🇹", callback_data="choose_italian")
german_button = InlineKeyboardButton("🇩🇪 Dutch 🇩🇪", callback_data="choose_dutch")
indian_button = InlineKeyboardButton("🇮🇳 Indian 🇮🇳", callback_data="choose_hindu")


commands_button = InlineKeyboardButton("⛓ Commands ⛓", callback_data="commands")
help_button = InlineKeyboardButton("🧚‍♂️ Help 🧚‍♂️", callback_data="help")
basic_commands_button = InlineKeyboardButton("⛓ Basic Commands ⛓", callback_data="basic_commands")
pro_commands_button = InlineKeyboardButton("⛓ Pro Commands ⛓", callback_data="pro_commands")


settings_button = InlineKeyboardButton("⚙️ Bot Settings ⚙️", callback_data="bot_settings")
enable_buy_alert = InlineKeyboardButton("🟤 Enable Buy Alerts", callback_data="enable_buy_alert")


permission_button = InlineKeyboardButton("🛡 Group Details 🛡", callback_data="detail")
banned_button = InlineKeyboardButton(f"💬 Set Banned Words 💬", callback_data="banned_words")
rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
spam_button = InlineKeyboardButton("📦 Spam 📦", callback_data="spam")
captcha_button = InlineKeyboardButton("🎩 Captcha 🎩", callback_data="captcha")
warning_button = InlineKeyboardButton("💢  Warning 💢", callback_data="warning")
media_button = InlineKeyboardButton("🧙 Media 🧙", callback_data="media")
tag_button = InlineKeyboardButton("🧑 Tag 🧑", callback_data="tag")
link_button = InlineKeyboardButton("🔗 Links 🔗", callback_data="links")
check_button = InlineKeyboardButton("✔ Checks ✔", callback_data="checks")
welcome_button = InlineKeyboardButton("📓 Welcome 📓", callback_data="welcome")
approval_button = InlineKeyboardButton("🍢 Approval 🍢", callback_data="approval")
# enable_subscription = InlineKeyboardButton("🟤 Enable Subscription", callback_data="enable_subscription")


support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")
website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    message_stack = get_message_stack(context)

    if is_group:
        group_data = await get_group(chat_id)
        LOGGER.debug(group_data)
        if group_data is not None:
            markup = [
                [support_button, website_button],
                [rules_button, help_button],
            ]
            keyboard = InlineKeyboardMarkup(markup)
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(
                chat_id=chat_id, text=help_message, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
    else:
        if not user.username:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await context.bot.send_message(
                chat_id=chat_id, text="👮 Please I require a username setup in your profile account."
            )
            return None

        markup = [
            [home_button],
            [add_button],
            [trade_button],
            [support_button, website_button],
            [settings_button],
            [language_button, help_button],
        ]
        keyboard = InlineKeyboardMarkup(markup)
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=help_message,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        except:
            await bot.send_message(
                chat_id=chat_id, text=help_message, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )

        message_content = {"chat_id": chat_id, "message": help_message, "keyboard": keyboard, "message_id": message_id}
        message_stack.append(message_content)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    # Fetch the bot's profile photo
    user_data = await get_user(user_id)

    if is_group:
        group_data = await get_group(chat_id)
        LOGGER.debug(group_data)
        if group_data is not None:
            markup = [
                [support_button, website_button],
                [rules_button, help_button],
            ]
            keyboard = InlineKeyboardMarkup(markup)
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(
                chat_id=chat_id, text=about_message, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
    else:
        markup = [
            [home_button],
            [add_button],
            [trade_button],
            [support_button, website_button],
            [settings_button],
            [language_button, help_button],
        ]
        keyboard = InlineKeyboardMarkup(markup)
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=about_message,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        except:
            await bot.send_message(
                chat_id=chat_id, text=about_message, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )

        message_content = {"chat_id": chat_id, "message": help_message, "keyboard": keyboard, "message_id": message_id}
        message_stack.append(message_content)







async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    # Fetch the bot's profile photo
    user_data = await get_user(user_id)

    if not is_group:
        markup = [
            # [cancel_button],
            [english_button, french_button],
            [german_button, indian_button],
            [italian_button, spanish_button],
            [back_button],
        ]

        keyboard = InlineKeyboardMarkup(markup)

        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Set a new language choice",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        except:
            await bot.send_message(
                chat_id=chat_id, text="Set a new language choice", reply_markup=keyboard, parse_mode=ParseMode.HTML
            )

        message_content = {"chat_id": chat_id, "message": help_message, "keyboard": keyboard, "message_id": message_id}
        message_stack.append(message_content)


async def choose_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type

    language = query.data[len("choose_") :]  # context.user_data.get('editing_group_chat_id')
    LOGGER.info(language)

    is_group = message_type in ("group", "supergroup", "channel")

    if not is_group:
        await update_user(user_id, {"chosen_language": language.title()})

        markup = [
            [add_button],
            [trade_button],
            [support_button, website_button],
            [settings_button],
            [language_button, help_button],
        ]
        keyboard = InlineKeyboardMarkup(markup)

        # Fetch the bot's profile photo
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"New language choice set to: <strong>{language.title()}</strong>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        except:
            await bot.send_message(
                chat_id=chat_id,
                text=f"New language choice set to: <strong>{language.title()}</strong>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )









async def ban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    bot = context.bot
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None and is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)

        group_data = await create_group(
            {
                "chat_id": chat_id,
                "group_name": group_name,
                "about": about,
            }
        )

    until_date = datetime.now() + timedelta(days=group_data["ban_duration"])

    admin = await GroupBotActions.get_group_member(GroupBotActions, chat_id, user_id, bot)
    LOGGER.info(admin)

    if is_group:

        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            # Extract the user ID from the command arguments
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)
            try:
                try:
                    banned_user_id = int(message.text.split()[1])
                    user_data = await get_user(banned_user_id)
                except Exception as e:
                    LOGGER.debug(str(e))
                    banned_user_id = str(message.text.split()[1])
                    user_data = await get_user_by_username(banned_user_id)

            except (IndexError, ValueError):
                # Handle invalid arguments
                await bot.send_message(
                    chat_id=user_id,
                    text="Invalid format. Please send <strong>/unban <user_id></strong>",
                    parse_mode=ParseMode.HTML,
                )
                return

            # Unban the user with the given ID
            # (Replace this with your actual unban code)
            await bot.ban_chat_member(
                chat_id=chat_id, user_id=user_data["user_id"], until_date=until_date, revoke_messages=True
            )

            # Send a confirmation message
            await bot.send_message(chat_id=chat_id, text=f"Banned user with ID: {user_data['username']}")
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=f"🤠 I see what you are trying to do. Please contact an admin to assist with this.",
            )


async def unban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    bot = context.bot
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None and is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)

        group_data = await create_group(
            {
                "chat_id": chat_id,
                "group_name": group_name,
                "about": about,
            }
        )

    admin = await GroupBotActions.get_group_member(GroupBotActions, chat_id, user_id, bot)
    LOGGER.info(admin)

    if is_group:

        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            # Extract the user ID from the command arguments
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)
            try:
                try:
                    banned_user_id = int(message.text.split()[1])
                    user_data = await get_user(banned_user_id)
                except Exception as e:
                    LOGGER.debug(str(e))
                    banned_user_id = str(message.text.split()[1])
                    user_data = await get_user_by_username(banned_user_id)
            except (IndexError, ValueError):
                # Handle invalid arguments
                await bot.send_message(
                    chat_id=user_id,
                    text="Invalid format. Please send <strong>/unban <user_id></strong>",
                    parse_mode=ParseMode.HTML,
                )
                return

            # Unban the user with the given ID
            # (Replace this with your actual unban code)
            await bot.unban_chat_member(chat_id=chat_id, user_id=user_data["user_id"])

            # Send a confirmation message
            await bot.send_message(chat_id=chat_id, text=f"Unbanned user with ID: {user_data['username']}")
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=f"🤠 I see what you are trying to do. Please contact an admin to assist with this.",
            )










async def on_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    user = update.message.new_chat_members[-1]
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")


    # Access relevant information about the latest chat member
    user_id = user.id

    group = await get_group(chat_id)

    if group is None and is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group = await create_group(
            {
                "chat_id": chat_id,
                "group_name": group_name,
                "about": about,
            }
        )

    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")


    markup = [
        [support_button, website_button],
        [rules_button, help_button],
    ]

    keyboard = InlineKeyboardMarkup(markup)

    if update.message.new_chat_members:  # Check if new members joined
        # Check if the bot itself is among the new members
        if context.bot.id == user_id or context.bot.id in [member.id for member in update.message.new_chat_members]:

            # Perform actions assuming bot was added
            await context.bot.send_message(
                chat_id=chat_id,
                text="Hi there! I'm excited to be part of this group. To set permissions and enable certain features please send a private message to me.",
                reply_markup=keyboard,
            )

            private_button = InlineKeyboardButton("🤖 Chat with me 🤖", url="https://t.me/modoraka_bot")

            markup = [
                [private_button],
            ]
            keyboard = InlineKeyboardMarkup(markup)
            # Perform actions assuming bot was added
            await context.bot.send_message(chat_id=chat_id, text="Send a message to me.", reply_markup=keyboard)
        else:
            expires = datetime.now() + timedelta(seconds=5)

            if not group["must_have_username"]:
                user_data = await get_user(user_id=user_id)
                if user_data is None:
                    data = {
                        "name": (
                            f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id
                        ),
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "username": user.username if user.username else user.user_id,
                        "subscribed": False,
                        "violated": False,
                        "chosen_language": user.language_code,
                    }
                    user_data = await create_user(data)
            else:
                if not user.username:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="Please we urge you to have a <strong>username</strong> filled to be a part of this group. Please NOTE: You have been removed until your username is setup.",
                        parse_mode=ParseMode.HTML,
                    )
                    await context.bot.ban_chat_member(
                        chat_id=chat_id, user_id=user_id, until_date=expires, revoke_messages=True
                    )
                    return None

                user_data = await get_user(user_id=user_id)
                if user_data is None:
                    data = {
                        "name": (
                            f"{user.first_name} {user.last_name}"
                            if user.first_name and user.last_name
                            else user.username
                        ),
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "username": user.username if user.username else user.user_id,
                        "subscribed": False,
                        "violated": False,
                        "chosen_language": "en",
                    }
                    user_data = await create_user(data)
                elif user.username != user_data["username"]:
                    data = {
                        "username": user.username if user.username else user.user_id,
                    }
                    user_data = await update_user(user_id, data)

            if group["enable_captcha"]:
                captcha_code = datetime.now() + timedelta(group["unverified_user_duration"])
                verify_captcha = InlineKeyboardButton(f"🗝 CODE: {captcha_code} 🗝", callback_data="verify_captcha")

                markup = [
                    [verify_captcha],
                ]

                keyboard = InlineKeyboardMarkup(markup)

                user_captcha = await get_captcah(chat_id, user_id)
                if user_captcha is None or not user_captcha["used"]:
                    await create_captcah(chat_id, user_id, int(captcha_code.timestamp()))
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo="https://www.shutterstock.com/image-illustration/3d-style-captcha-test-green-600nw-2308935989.jpg",
                        caption=f"To complete your verification into the group you have to ensure the code in the button below corresponds to the code in the text below. If yes click on it to verify you are no robot.\n\nCODE: {captcha_code}",
                        reply_markup=markup,
                        parse_mode=ParseMode.HTML,
                    )
                    await context.bot.ban_chat_member(
                        chat_id=chat_id, user_id=user_id, until_date=expires, revoke_messages=True
                    )
                    return None

            welcome_message = (
                group["welcome_message"]
                if group["welcome_message"]
                else "Hi there, You are welcome. Please take the time to read through the rules governing this group so as to prevent me from taking actions against you for violating them. Thank You!"
            )
            await context.bot.send_message(chat_id=chat_id, text=welcome_message, reply_markup=keyboard)


async def start_command(update: Update, context: CallbackContext):
    context.user_data.clear()
    ConversationHandler.END

    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type

    LOGGER.info(f"Start Chat Type: {message_type}")
    is_group = message_type in ("group", "supergroup", "channel")

    message_stack = get_message_stack(context)

    LOGGER.info(user_id)

    if not user.username:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="👮 Please I require a username setup in your profile account. run /start again when you are done setting up your username.",
            parse_mode=ParseMode.HTML,
        )
        return None

    user_data = await get_user(user_id=user_id)
    if user_data is None:
        data = {
            "name": f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
            "chat_id": chat_id,
            "user_id": user_id,
            "username": user.username if user.username else user.user_id,
            "subscribed": False,
            "violated": False,
            "chosen_language": user.language_code,
        }
        user_data = await create_user(data)


    markup = [
        [add_button],
        [trade_button],
        [support_button, website_button],
        [settings_button],
        [language_button, help_button],
    ]



    # markup = await generate_button(command_name="start", user=user_data, is_group=is_group)
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    keyboard = InlineKeyboardMarkup(markup)
    message_content = {"chat_id": chat_id, "message": home_message, "keyboard": keyboard, "message_id": message_id}

    # Push new message content to the stack
    message_stack.append(message_content)

    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=home_message, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )
    except:
        await context.bot.send_message(
            chat_id=chat_id,
            text=home_message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )


async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_stack = get_message_stack(context)

    if len(message_stack) > 0:
        message = message_stack[-1]
        await context.bot.edit_message_text(
            text=message["message"],
            chat_id=message["chat_id"],
            message_id=message["message_id"],
            parse_mode=ParseMode.HTML,
            reply_markup=message["keyboard"],
        )
        message_stack.pop()









RULES_EDIT_SAVE = range(1)
async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    context.user_data["editing_group_chat_id"] = chat_id

    # Fetch the bot's profile photo
    user_data = await get_user(user_id)
    if user_data is None:
        data = {
            "name": f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
            "chat_id": chat_id,
            "user_id": user_id,
            "username": user.username if user.username else user.user_id,
            "subscribed": False,
            "violated": False,
            "chosen_language": user.language_code,
        }
        user_data = await create_user(data)

    if is_group:
        group_data = await get_group(chat_id)
        if group_data is None:
            admins = await GroupBotActions.get_all_administrators(GroupBotActions, chat_id, bot)
            group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
            about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)

            group_data = await create_group(
                {
                    "chat_id": chat_id,
                    "group_name": group_name,
                    "about": about,
                }
            )
        await update_user_group(user_id, chat_id)
    else:
        group_id = context.user_data.get('selected_group')
        group_data = await get_group(group_id)
        if group_data is None:
            await bot.send_message(chat_id=chat_id, text="You must add me to a group to enjoy my powers")
            return None

        await update_user_group(user_id, group_id)

    message = f"I am not aware of a predefined rule-set for this group. <strong>Please inform an admin to set this up for me.</strong>"
    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    delete_rules_button = InlineKeyboardButton("🚫 Delete Rules 🚫", callback_data=f"delete_rules-{group_data['chat_id']}")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")

    set_rules_button = InlineKeyboardButton("✏ Set Rules ✏", callback_data=f"set_rules-{group_data['chat_id']}")
    admin = await GroupBotActions.get_group_member(GroupBotActions, group_data['chat_id'], user_id, bot)
    if group_data["about"] == ("" or None):
        markup = [
            [set_rules_button, delete_rules_button],
            [support_button, website_button],
            [language_button, help_button],
        ]

        keyboard = InlineKeyboardMarkup(markup)


        markup_II = [
            [home_button],
            [support_button, website_button],
            [help_button],
        ]
        if is_group:
            markup_II = [
                [support_button, website_button],
                [help_button],
            ]
        keyboard_II = InlineKeyboardMarkup(markup_II)

        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, group_data['chat_id'])
            # Perform actions assuming bot was added
            # message_stack = get_message_stack(context)
            # message_content = {"chat_id": chat_id, "message": message, "markup": markup, "message_id": message_id}
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await bot.send_message(
                chat_id=user_id,
                text=f"<strong>{group_name.title()}</strong>\n\nPlease add the regulations governing this group",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )

        else:
            for ad in admins:
                if not ad.user.is_bot:
                    await bot.send_chat_action(chat_id=ad.user.id, action=ChatAction.TYPING)
                    await bot.send_message(
                        chat_id=ad.user.id,
                        text=f"<strong>{group_name.title()}</strong>\n\nPlease add the regulations governing this group",
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML,
                    )

            try:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                await bot.edit_message_text(
                    chat_id=group_data['chat_id'],
                    message_id=message_id,
                    text="🤖🤖🤖🤖🤖\n\nI'm Sorry to break this to you, but we currently do not have a rule set. An admin has been alerted for this.",
                    reply_markup=keyboard_II,
                    parse_mode=ParseMode.HTML,
                )
            except:
                await bot.send_chat_action(chat_id=group_data['chat_id'], action=ChatAction.TYPING)
                await bot.delete_message(chat_id=group_data['chat_id'], message_id=message_id)
                await bot.send_message(
                    chat_id=group_data['chat_id'],
                    text="🤖🤖🤖🤖🤖\n\nI'm Sorry to break this to you, but we currently do not have a rule set. An admin has been alerted for this.",
                    reply_markup=keyboard_II,
                    parse_mode=ParseMode.HTML,
                )

    elif group_data is not None and group_data["about"] != ("" or None):
        message = group_data["about"]
        markup = [
            [home_button],
            [set_rules_button, delete_rules_button],
            [support_button, website_button],
            [language_button, help_button],
        ]

        markup_II = [
            [home_button],
            [support_button, website_button],
            [help_button],
        ]
        if is_group:
            markup = [
                [set_rules_button, delete_rules_button],
                [support_button, website_button],
                [language_button, help_button],
            ]

            markup_II = [
                [support_button, website_button],
                [help_button],
            ]

        keyboard = InlineKeyboardMarkup(markup)
        keyboard_II = InlineKeyboardMarkup(markup_II)

        # Perform actions assuming bot was added
        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)
            # Perform actions assuming bot was added
            # message_stack = get_message_stack(context)
            # message_content = {"chat_id": chat_id, "message": message, "markup": markup, "message_id": message_id}

            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message,
                reply_markup=keyboard_II,
                parse_mode=ParseMode.HTML,
            )
            await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            try:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=message,
                    reply_markup=keyboard_II,
                    parse_mode=ParseMode.HTML,
                )
            except:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                await bot.send_message(
                    chat_id=chat_id, text=message, reply_markup=keyboard_II, parse_mode=ParseMode.HTML
                )

async def set_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    group_id = query.data[len("set_rules-") :]  # context.user_data.get('editing_group_chat_id')
    if group_id is None:
        group_id = context.user_data.get('selected_group')
    context.user_data["editing_group_chat_id"] = group_id
    LOGGER.debug(f"Argument for Group ID: {group_id}")

    group_data = await get_group(group_id)

    if group_data is None and is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group_data = await create_group(
            {
                "chat_id": group_id,
                "group_name": group_name,
                "about": about,
            }
        )

    admin = await GroupBotActions.get_group_member(GroupBotActions, group_id, user_id, bot)

    if not is_group:
        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, group_id)

            message = f"Please paste your rules in the input box."
            if group_data is not None and group_data["about"] != ("" or None):
                message = group_data["about"]

            # Perform actions assuming bot was added
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=ForceReply(selective=False, input_field_placeholder="Type or Paste your rules here."),
                parse_mode=ParseMode.HTML,
            )
            return RULES_EDIT_SAVE
        else:
            ConversationHandler.END
            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [[support_button, website_button], [rules_button]]
            keyboard = InlineKeyboardMarkup(markup)
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="You are not an admin in this group. Nice try mate! 😂",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )


async def save_set_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group_id = context.user_data.get("editing_group_chat_id")
    LOGGER.debug(f"Save Rules Group ID: {group_id}")

    data = {"about": text}
    LOGGER.debug(text)

    group_data = await update_group(group_id, data)

    user_data = await get_user(user_id=user_id)
    if user_data is None:
        data = {
            "name": f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
            "chat_id": chat_id,
            "user_id": user_id,
            "username": user.username if user.username else user.user_id,
            "subscribed": False,
            "violated": False,
            "chosen_language": user.language_code,
        }
        user_data = await create_user(data)

    message = group_data["about"]

    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

    markup = [[rules_button, website_button], [support_button]]
    keyboard = InlineKeyboardMarkup(markup)

    await bot.send_chat_action(chat_id=group_id, action=ChatAction.TYPING)
    await bot.send_message(chat_id=group_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    ConversationHandler.END


async def delete_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    group_id = query.data[len("delete_rules-") :]  # context.user_data.get('editing_group_chat_id')
    if group_id is None:
        group_id = context.user_data.get('selected_group')
    admin = await GroupBotActions.get_group_member(GroupBotActions, group_id, user_id, bot)

    if not is_group:
        user_data = await get_user(user_id)

        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)

            data = {"about": None}

            await update_group(group_id, data)

            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [[rules_button, website_button], [support_button]]
            keyboard = InlineKeyboardMarkup(markup)

            # Perform actions assuming bot was added
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Your bot's rules has been removed",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        else:
            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [[rules_button, website_button], [support_button]]
            keyboard = InlineKeyboardMarkup(markup)
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="You are not an admin in this group. Nice try mate! 😂",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )








async def intervention_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None and is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group_data = await create_group(
            {
                "chat_id": chat_id,
                "group_name": group_name,
                "about": about,
            }
        )

    admin = await GroupBotActions.get_group_member(GroupBotActions, chat_id, user_id, bot)

    admins = await GroupBotActions.get_all_administrators(GroupBotActions, chat_id, bot)

    if is_group:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)

        if admin.status not in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR) and not admin.user.is_bot:
            # Extract the user ID from the command arguments
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)

            try:
                banned_user_id = str(message.text.split()[1])
                admin_data = await get_user_by_username(banned_user_id)
                await bot.send_message(
                    chat_id=admin_data["user_id"],
                    text=f"<code>FROM: {group_name.title()}</code>\n\nPlease respond to @{user_data['username'] if user_data['username'] else update.message.from_user.username}. He/She has a reason for you to intevene.",
                    parse_mode=ParseMode.HTML,
                )
                # Send a confirmation message
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"@{admin_data['username'].title()}\n\nWould respond to you immeditely they get you message.",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                LOGGER.info(e)
                for ad in admins:
                    user_data = await get_user(user_id)
                    if not ad.user.is_bot:
                        await bot.send_message(
                            chat_id=ad.user.id,
                            text=f"<code>FROM: {group_name.title()}</code>\n\nPlease respond to @{user_data['username']}. He/She has a reason for you to intevene.",
                            parse_mode=ParseMode.HTML,
                        )
                # Send a confirmation message
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"@{user_data['username'] if user_data['username'] else update.message.from_user.username} An admin would respond to you privately.",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await bot.send_message(chat_id=chat_id, text=f"🤠 you are already an admin. What would you like to do?")






async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    user_groups = await view_user_groups(user_id)


    if len(user_groups['groups']) > 0:
        markup = [
            [home_button],
        ]
        LOGGER.info(user_groups['groups'])
        for group in user_groups['groups']:
            group_button = InlineKeyboardButton(f"👪 {group['name'] if group['name'] else group['chat_id']} 👪", callback_data=f"group-{group['chat_id']}")
            markup.append([group_button])

        keyboard = InlineKeyboardMarkup(markup)

        message = "Select a group to set banned words"
        message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
        # Push new message content to the stack
        message_stack.append(message_content)
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard)
    else:
        markup = [
            [add_button],
            [trade_button],
            [support_button, website_button],
            [settings_button],
            [language_button, help_button],
        ]

        # markup = await generate_button(command_name="start", user=user_data, is_group=is_group)
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        keyboard = InlineKeyboardMarkup(markup)
        # Push new message content to the stack
        message = "Add me to a group first"
        message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
        message_stack.append(message_content)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard)


async def set_selected_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    group_id = query.data[len("group-") :]
    context.user_data['selected_group'] = group_id

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    user_data = await get_user(user_id=user_id)

    message = f"""
From here you can adjust whatever settings you desire for your group and the bot would perform them automatically for you.
    """

    markup = [
        [home_button],
        [permission_button, banned_button],
        [rules_button, spam_button],
        [captcha_button, warning_button],
        [media_button, tag_button],
        [link_button, check_button],
        [welcome_button, approval_button],
        [enable_buy_alert]
    ]

    context.user_data['saved_message_id'] = message_id

    keyboard = InlineKeyboardMarkup(markup)

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard)
    message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    message_stack.append(message_content)




SAVE_BANNED_WORDS = range(1)
async def set_banned_words_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")
    group_id = context.user_data.get('selected_group')

    words = await get_banned_words(group_id)
    banned_words = words

    context.user_data['open_banned_words_message_id'] = message_id


    message = f"""
    Type/Paste the words seperated with a comma for multiple words.

WORDS:
{banned_words['words']}

    """

    keyboard = ForceReply(selective=False, input_field_placeholder="Paste your words")
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    context.user_data['bot_add_banned_word_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
    return SAVE_BANNED_WORDS
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def save_banned_words_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_stack = get_message_stack(context)

    group_id = context.user_data.get('selected_group')
    LOGGER.debug(f"Save Rules Group ID: {group_id}")

    main_id = context.user_data.get('open_banned_words_message_id')
    update_id = context.user_data.get('bot_add_banned_word_message_id')


    words = await update_banned_words(group_id, text)
    banned_words = words

    markup = [
        [home_button],
        [permission_button, banned_button],
        [rules_button, spam_button],
        [captcha_button, warning_button],
        [media_button, tag_button],
        [link_button, check_button],
        [welcome_button, approval_button],
        [enable_buy_alert]
    ]
    keyboard = InlineKeyboardMarkup(markup)
    message = f"Banned Words set {banned_words['words']}"

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=update_id.message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=main_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END





async def set_captcha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    captcha_button = InlineKeyboardButton(f"{'✔ Disable Captcha' if group['enable_captcha'] else '✖ Enable Captcha'}", callback_data=f"captcha-{'true' if not group['enable_captcha'] else 'false'}")
    captch_timestamp_button1 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 1 else ''} 1 Secs", callback_data="captcha-1")
    captch_timestamp_button2 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 2 else ''} 2 Secs", callback_data="captcha-2")
    captch_timestamp_button3 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 3 else ''} 3 Secs", callback_data="captcha-3")
    captch_timestamp_button4 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 4 else ''} 4 Secs", callback_data="captcha-4")
    captch_timestamp_button5 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 5 else ''} 5 Secs", callback_data="captcha-5")
    captch_timestamp_button6 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 6 else ''} 6 Secs", callback_data="captcha-6")
    captch_timestamp_button7 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 7 else ''} 7 Secs", callback_data="captcha-7")

    markup = [
        [captcha_button],
        [captch_timestamp_button1, captch_timestamp_button2, captch_timestamp_button3, captch_timestamp_button4, captch_timestamp_button5, captch_timestamp_button6, captch_timestamp_button7],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Captcha Settings</strong>
To ensure random bots do not join and spam your group you can enable a captcha option to have this done.
Now whenever a new member joins they would be made to provide an otp code for the verification and that will be used to authenticate the new member and allow them join the group. If the user fails to verify within a set time frame the authentication code will become invalid.

Captcha: {'✔ Enabled' if group['enable_captcha'] else '✖ Disabled'}
Expiry Duration: {group['unverified_user_duration']} Seconds
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_captcha_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    message_stack = get_message_stack(context)

    if re.match(r"^captcha-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^captcha-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"enable_captcha":enable}
    elif not re.match(r"^captcha-(.*?)", command).group(1) in ['true', 'false']:
        seconds = int(query.data[len("captcha-") :])
        LOGGER.info(seconds)
        data = {"unverified_user_duration":seconds}

    group = await update_group(group_id, data)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    captcha_button = InlineKeyboardButton(f"{'✔ Disable Captcha' if group['enable_captcha'] else '✖ Enable Captcha'}", callback_data=f"captcha-{'true' if not group['enable_captcha'] else 'false'}")
    captch_timestamp_button1 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 1 else ''} 1 Secs", callback_data="captcha-1")
    captch_timestamp_button2 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 2 else ''} 2 Secs", callback_data="captcha-2")
    captch_timestamp_button3 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 3 else ''} 3 Secs", callback_data="captcha-3")
    captch_timestamp_button4 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 4 else ''} 4 Secs", callback_data="captcha-4")
    captch_timestamp_button5 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 5 else ''} 5 Secs", callback_data="captcha-5")
    captch_timestamp_button6 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 6 else ''} 6 Secs", callback_data="captcha-6")
    captch_timestamp_button7 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 7 else ''} 7 Secs", callback_data="captcha-7")

    markup = [
        [captcha_button],
        [captch_timestamp_button1, captch_timestamp_button2, captch_timestamp_button3, captch_timestamp_button4, captch_timestamp_button5, captch_timestamp_button6, captch_timestamp_button7],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)


    message = f"""
<strong>Captcha Settings</strong>
To ensure random bots do not join and spam your group you can enable a captcha option to have this done.
Now whenever a new member joins they would be made to provide an otp code for the verification and that will be used to authenticate the new member and allow them join the group. If the user fails to verify within a set time frame the authentication code will become invalid.

Captcha: {'✔ Enabled' if group['enable_captcha'] else '✖ Disabled'}
Expiry Duration: {group['unverified_user_duration']} Seconds
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)




async def set_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    username_button = InlineKeyboardButton(f"{'✔ Disable Username Check' if group['must_have_username'] else '✖ Enable Username Check'}", callback_data=f"checks-{'true' if not group['must_have_username'] else 'false'}")
    group_about_button = InlineKeyboardButton(f"{'✔ Disable Group-About Check' if group['must_have_about'] else '✖ Enable Group-About Check'}", callback_data=f"checks-{'true' if not group['must_have_about'] else 'false'}")
    group_desc_button = InlineKeyboardButton(f"{'✔ Disable Group-Desc Check' if group['must_have_description'] else '✖ Enable Group-Desc Check'}", callback_data=f"checks-{'true' if not group['must_have_description'] else 'false'}")
    markup = [
        [username_button],
        [group_about_button],
        [group_desc_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Username Check: {'✔ Enabled' if group['must_have_username'] else '✖ Disabled'}
Group-About Check: {'✔ Enabled' if group['must_have_about'] else '✖ Disabled'}
Group-Desc Check: {'✔ Enabled' if group['must_have_description'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_check_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    message_stack = get_message_stack(context)

    if re.match(r"^checks_username-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^checks_username-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"must_have_username":enable}
    elif re.match(r"^checks_about-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^checks_about-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"must_have_about":enable}
    elif re.match(r"^checks_description-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^checks_description-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"must_have_description":enable}

    group = await update_group(group_id, data)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    username_button = InlineKeyboardButton(f"{'✔ Disable Username Check' if group['must_have_username'] else '✖ Enable Username Check'}", callback_data=f"checks-{'true' if not group['must_have_username'] else 'false'}")
    group_about_button = InlineKeyboardButton(f"{'✔ Disable Group-About Check' if group['must_have_about'] else '✖ Enable Group-About Check'}", callback_data=f"checks-{'true' if not group['must_have_about'] else 'false'}")
    group_desc_button = InlineKeyboardButton(f"{'✔ Disable Group-Desc Check' if group['must_have_description'] else '✖ Enable Group-Desc Check'}", callback_data=f"checks-{'true' if not group['must_have_description'] else 'false'}")
    markup = [
        [username_button],
        [group_about_button],
        [group_desc_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Username Check: {'✔ Enabled' if group['must_have_username'] else '✖ Disabled'}
Group-About Check: {'✔ Enabled' if group['must_have_about'] else '✖ Disabled'}
Group-Desc Check: {'✔ Enabled' if group['must_have_description'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)






async def set_warning_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    delete_messages_button = InlineKeyboardButton(f"{'✔ Disable Group-Delete Messages' if group['delete_messages'] else '✖ Enable Group-Delete Messages'}", callback_data=f"warning-{'true' if not group['delete_messages'] else 'false'}")
    max_warnings_button1 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 1 else ''}1", callback_data=f"warning-1")
    max_warnings_button2 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 2 else ''}2", callback_data=f"warning-2")
    max_warnings_button3 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 3 else ''}3", callback_data=f"warning-3")
    max_warnings_button4 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 4 else ''}4", callback_data=f"warning-4")
    max_warnings_button5 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 5 else ''}5", callback_data=f"warning-5")
    mute_duration_button = InlineKeyboardButton("Mute Duration", callback_data=f"warnings-mute_duration")
    ban_duration_button = InlineKeyboardButton("Ban Duration", callback_data=f"warnings-ban_duration")
    max_message_length_button = InlineKeyboardButton("Group-max Message Length", callback_data=f"warnings-max_length")
    markup = [
        [mute_duration_button],
        [ban_duration_button],
        [max_message_length_button],
        [delete_messages_button],
        [max_warnings_button1, max_warnings_button2, max_warnings_button3, max_warnings_button4, max_warnings_button5],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Max Warning before Block: {group['max_warnings']}
Mute Duration: {group['mute_duration']}
Ban Duration: {group['ban_duration']}
Group-max Message Lengt: {group['max_message_length']}
Group-Delete Messages: {'✔ Enabled' if group['delete_messages'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_warning_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_stack = get_message_stack(context)

    context.user_data['warning_message_id'] = message_id
    LOGGER.info(query.data[len("warning-") :])

    if query.data[len("warning-") :] in ['true', 'false']:
        enable = False
        if query.data[len("warning-") :] == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"delete_messages":enable}
        group = await update_group(group_id, data)
    elif not re.match(r"^warning-(.*?)", command) in ['true', 'false']:
        value = int(query.data[len("warning-") :])
        LOGGER.info(value)
        data = {"max_warnings":int(value)}
        group = await update_group(group_id, data)


    group = await get_group(group_id)

    delete_messages_button = InlineKeyboardButton(f"{'✔ Disable Group-Delete Messages' if group['delete_messages'] else '✖ Enable Group-Delete Messages'}", callback_data=f"warning-{'true' if not group['delete_messages'] else 'false'}")
    max_warnings_button1 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 1 else ''}1", callback_data=f"warning-1")
    max_warnings_button2 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 2 else ''}2", callback_data=f"warning-2")
    max_warnings_button3 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 3 else ''}3", callback_data=f"warning-3")
    max_warnings_button4 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 4 else ''}4", callback_data=f"warning-4")
    max_warnings_button5 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 5 else ''}5", callback_data=f"warning-5")
    mute_duration_button = InlineKeyboardButton("Mute Duration", callback_data=f"warnings-mute_duration")
    ban_duration_button = InlineKeyboardButton("Ban Duration", callback_data=f"warnings-ban_duration")
    max_message_length_button = InlineKeyboardButton("Group-max Message Length", callback_data=f"warnings-max_length")
    markup = [
        [mute_duration_button],
        [ban_duration_button],
        [max_message_length_button],
        [delete_messages_button],
        [max_warnings_button1, max_warnings_button2, max_warnings_button3, max_warnings_button4, max_warnings_button5],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Max Warning before Block: {group['max_warnings']}
Mute Duration: {group['mute_duration']}
Ban Duration: {group['ban_duration']}
Group-max Message Lengt: {group['max_message_length']}
Group-Delete Messages: {'✔ Enabled' if group['delete_messages'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

WARNING_SETTING = range(1)
async def update_warnings_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_stack = get_message_stack(context)

    context.user_data['warning_message_id'] = message_id

    if re.match(r"^warnings-(\w+)", command).group(1) == "mute_duration":
        message = "Type out the mute_duration in figure"
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message)
        context.user_data['editing'] = "mute_duration"
        return WARNING_SETTING
    elif re.match(r"^warnings-(\w+)", command).group(1) == "ban_duration":
        message = "Type out the ban_duration in figure"
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message)
        context.user_data['editing'] = "ban_duration"
        return WARNING_SETTING
    elif re.match(r"^warnings-(\w+)", command).group(1) == "max_length":
        message = "Type out the max_message_length in figure"
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message)
        context.user_data['editing'] = "max_message_length"
        return WARNING_SETTING

    group = await get_group(group_id)

    max_warnings_button1 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 1 else ''}1", callback_data=f"warning-1")
    max_warnings_button2 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 2 else ''}2", callback_data=f"warning-2")
    max_warnings_button3 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 3 else ''}3", callback_data=f"warning-3")
    max_warnings_button4 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 4 else ''}4", callback_data=f"warning-4")
    max_warnings_button5 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 5 else ''}5", callback_data=f"warning-5")
    mute_duration_button = InlineKeyboardButton("Mute Duration", callback_data=f"warnings-mute_duration")
    ban_duration_button = InlineKeyboardButton("Ban Duration", callback_data=f"warnings-ban_duration")
    max_message_length_button = InlineKeyboardButton("Group-max Message Length", callback_data=f"warnings-max_length")
    delete_messages_button = InlineKeyboardButton(f"{'✔ Disable Group-Delete Messages' if group['delete_messages'] else '✖ Enable Group-Delete Messages'}", callback_data=f"warning-{'true' if not group['delete_messages'] else 'false'}")
    markup = [
        [mute_duration_button],
        [ban_duration_button],
        [max_message_length_button],
        [delete_messages_button],
        [max_warnings_button1, max_warnings_button2, max_warnings_button3, max_warnings_button4, max_warnings_button5],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Max Warning before Block: {group['max_warnings']}
Mute Duration: {group['mute_duration']}
Ban Duration: {group['ban_duration']}
Group-max Message Lengt: {group['max_message_length']}
Group-Delete Messages: {'✔ Enabled' if group['delete_messages'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def update_warnings_para_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    bot_warning_message_id = context.user_data.get('bot_warning_message_id').message_id
    warning_message_id = context.user_data.get('warning_message_id')
    message_stack = get_message_stack(context)
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    data = {"mute_duration": int(text)}
    if context.user_data.get('editing') == "ban_duration":
            data = {"ban_duration": int(text)}
    elif context.user_data.get('editing') == "max_message_length":
            data = {"max_message_length": int(text)}
    await update_group(group_id, data)
    group = await get_group(group_id)

    max_warnings_button1 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 1 else ''}1", callback_data=f"warning-1")
    max_warnings_button2 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 2 else ''}2", callback_data=f"warning-2")
    max_warnings_button3 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 3 else ''}3", callback_data=f"warning-3")
    max_warnings_button4 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 4 else ''}4", callback_data=f"warning-4")
    max_warnings_button5 = InlineKeyboardButton(f"{'✔ ' if group['max_warnings'] == 5 else ''}5", callback_data=f"warning-5")
    mute_duration_button = InlineKeyboardButton("Mute Duration", callback_data=f"warnings-mute_duration")
    ban_duration_button = InlineKeyboardButton("Ban Duration", callback_data=f"warnings-ban_duration")
    max_message_length_button = InlineKeyboardButton("Group-max Message Length", callback_data=f"warnings-max_length")
    delete_messages_button = InlineKeyboardButton(f"{'✔ Disable Group-Delete Messages' if group['delete_messages'] else '✖ Enable Group-Delete Messages'}", callback_data=f"warning-{'true' if not group['delete_messages'] else 'false'}")
    markup = [
        [mute_duration_button],
        [ban_duration_button],
        [max_message_length_button],
        [delete_messages_button],
        [max_warnings_button1, max_warnings_button2, max_warnings_button3, max_warnings_button4, max_warnings_button5],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Registration Checks</strong>
To ensure groups and users are properly interated into the system we provide a means to enforce a check to prevent anyone without a valid bio information from getting access to the bot.

Max Warning before Block: {group['max_warnings']}
Mute Duration: {group['mute_duration']}
Ban Duration: {group['ban_duration']}
Group-max Message Lengt: {group['max_message_length']}
Group-Delete Messages: {'✔ Enabled' if group['delete_messages'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=bot_warning_message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=warning_message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)






async def set_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    group_name_button = InlineKeyboardButton("Group Name", callback_data="group_name")
    about_button = InlineKeyboardButton("Group Description", callback_data="about")
    website_button = InlineKeyboardButton("Group Official Website", callback_data="website")
    support_button = InlineKeyboardButton("Group Telegram Support", callback_data="support")
    markup = [
        [group_name_button],
        [about_button],
        [website_button],
        [support_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Group Details</strong>
Adjust the information you intend for the bot to use when representing your group

Group Name: {group['group_name']}
Group Description: {group['about']}
Group Official Website: {group['website']}
Group Telegram Support: {group['support']}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

DETAIL_SETTING = range(1)
async def update_details_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_stack = get_message_stack(context)

    context.user_data['warning_message_id'] = message_id
    group = await get_group(group_id)

    if command == "group_name":
        message = "Add a group name" if not group['group_name'] else group['group_name']
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Add a group name"))
        context.user_data['editing'] = "group_name"
        return DETAIL_SETTING
    elif command == "about":
        message = "Add group description" if not group['about'] else group['about']
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Add group description"))
        context.user_data['editing'] = "about"
        return DETAIL_SETTING
    elif command == "website":
        message = "Add group website" if not group['website'] else group['website']
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Add group website"))
        context.user_data['editing'] = "website"
        return DETAIL_SETTING
    elif command == "support":
        message = "Add group telegram support account link" if not group['support'] else group['support']
        context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Add group telegram support account link"))
        context.user_data['editing'] = "support"
        return DETAIL_SETTING

async def save_details_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    bot_warning_message_id = context.user_data.get('bot_warning_message_id').message_id
    warning_message_id = context.user_data.get('warning_message_id')
    message_stack = get_message_stack(context)
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    data = {"group_name": text}
    if context.user_data.get('editing') == "about":
        data = {"about": text}
    elif context.user_data.get('editing') == "website":
        data = {"website": text}
    elif context.user_data.get('editing') == "support":
        data = {"support": text}
    await update_group(group_id, data)
    group = await get_group(group_id)

    group_name_button = InlineKeyboardButton("Group Name", callback_data="group_name")
    about_button = InlineKeyboardButton("Group Description", callback_data="about")
    website_button = InlineKeyboardButton("Group Official Website", callback_data="website")
    support_button = InlineKeyboardButton("Group Telegram Support", callback_data="support")
    markup = [
        [group_name_button],
        [about_button],
        [website_button],
        [support_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Group Details</strong>
Adjust the information you intend for the bot to use when representing your group

Group Name: {group['group_name']}
Group Description: {group['about']}
Group Official Website: {group['website']}
Group Telegram Support: {group['support']}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=bot_warning_message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=warning_message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)





async def set_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    token = await get_token_watched(group_id)

    watch_name_button = InlineKeyboardButton("Token Symbol", callback_data="symbol")
    markup = [
        [watch_name_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Buy Alert Details</strong>
Adjust the information if you need to adjust which token you watch

Token Symbol: {token['token']['token_symbol']}
Token Name: {token['token']['token_name']}
Token Supply: {token['token']['total_supply']}
Token Circulating Supply: {token['token']['token_circulating_supply']}
Token USD Price: {token['token']['token_usd_price']}
Token Address: {token['token']['token_address']}
    """ if token is not None else "Add a token"

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

TOKEN_SETTING = range(1)
async def update_token_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_stack = get_message_stack(context)

    context.user_data['warning_message_id'] = message_id

    message = "What is your token symbol?"
    context.user_data['bot_warning_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="BTC, ETH, USDT...?"))
    return TOKEN_SETTING

async def save_token_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    bot_warning_message_id = context.user_data.get('bot_warning_message_id').message_id
    warning_message_id = context.user_data.get('warning_message_id')
    message_stack = get_message_stack(context)
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    data = {"about": text}
    token = await create_tokens_watched(group_id, text)

    watch_name_button = InlineKeyboardButton("Token Symbol", callback_data="symbol")
    markup = [
        [watch_name_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Buy Alert Details</strong>
Adjust the information if you need to adjust which token you watch

Token Symbol: {token['token']['token_symbol']}
Token Name: {token['token']['token_name']}
Token Supply: {token['token']['total_supply']}
Token Circulating Supply: {token['token']['token_circulating_supply']}
Token USD Price: {token['token']['token_usd_price']}
Token Address: {token['token']['token_address']}
    """ if token is not None else "Add a token"

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=bot_warning_message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=warning_message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)







async def set_tagging_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    tagging_button = InlineKeyboardButton(f"{'✔ Disable Tagging' if group['allow_hash'] else '✖ Enable Tagging'}", callback_data=f"tagging-{'true' if not group['allow_hash'] else 'false'}")
    mention_button = InlineKeyboardButton(f"{'✔ Disable Mentioning' if group['allow_mention'] else '✖ Enable Mention'}", callback_data=f"mention-{'true' if not group['allow_mention'] else 'false'}")
    markup = [
        [tagging_button, mention_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Tagging Settings</strong>
To ensure random mentions or hashtags are not circulated within your group please adjust these settings as you deem fit

Prevent Hash Tagging: {'✔ Enabled' if group['allow_hash'] else '✖ Disabled'}
Prevent Mentions: {'✔ Enabled' if group['allow_mention'] else '✖ Disabled'}
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_tagging_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    message_stack = get_message_stack(context)

    if re.match(r"^tagging-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^tagging-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"allow_hash":enable}

    group = await update_group(group_id, data)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    tagging_button = InlineKeyboardButton(f"{'✔ Disable Tagging' if group['allow_hash'] else '✖ Enable Tagging'}", callback_data=f"tagging-{'true' if not group['allow_hash'] else 'false'}")
    mention_button = InlineKeyboardButton(f"{'✔ Disable Mentioning' if group['allow_mention'] else '✖ Enable Tagging'}", callback_data=f"mention-{'true' if not group['allow_mention'] else 'false'}")
    markup = [
        [tagging_button, mention_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Tagging Settings</strong>
To ensure random mentions or hashtags are not circulated within your group please adjust these settings as you deem fit

Prevent Hash Tagging: {'✔ Enabled' if group['allow_hash'] else '✖ Disabled'}
Prevent Mentions: {'✔ Enabled' if group['allow_mention'] else '✖ Disabled'}
    """


    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def update_mention_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    message_stack = get_message_stack(context)

    if re.match(r"^mention-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^mention-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"allow_mention":enable}

    group = await update_group(group_id, data)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    tagging_button = InlineKeyboardButton(f"{'✔ Disable Tagging' if group['allow_hash'] else '✖ Enable Tagging'}", callback_data=f"tagging-{'true' if not group['allow_hash'] else 'false'}")
    mention_button = InlineKeyboardButton(f"{'✔ Disable Mentioning' if group['allow_mention'] else '✖ Enable Tagging'}", callback_data=f"mention-{'true' if not group['allow_mention'] else 'false'}")
    markup = [
        [tagging_button, mention_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Tagging Settings</strong>
To ensure random mentions or hashtags are not circulated within your group please adjust these settings as you deem fit

Prevent Hash Tagging: {'✔ Enabled' if group['allow_hash'] else '✖ Disabled'}
Prevent Mentions: {'✔ Enabled' if group['allow_mention'] else '✖ Disabled'}
    """


    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)





# TODO: Fix the media commands
async def set_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id

    captcha_button = InlineKeyboardButton(f"{'✔ Disable Captcha' if group['enable_captcha'] else '✖ Enable Captcha'}", callback_data=f"captcha-{'true' if not group['enable_captcha'] else 'false'}")
    captch_timestamp_button1 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 1 else ''} 1 Secs", callback_data="captcha-1")
    captch_timestamp_button2 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 2 else ''} 2 Secs", callback_data="captcha-2")
    captch_timestamp_button3 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 3 else ''} 3 Secs", callback_data="captcha-3")
    captch_timestamp_button4 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 4 else ''} 4 Secs", callback_data="captcha-4")
    captch_timestamp_button5 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 5 else ''} 5 Secs", callback_data="captcha-5")
    captch_timestamp_button6 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 6 else ''} 6 Secs", callback_data="captcha-6")
    captch_timestamp_button7 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 7 else ''} 7 Secs", callback_data="captcha-7")

    markup = [
        [captcha_button],
        [captch_timestamp_button1, captch_timestamp_button2, captch_timestamp_button3, captch_timestamp_button4, captch_timestamp_button5, captch_timestamp_button6, captch_timestamp_button7],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Captcha Settings</strong>
To ensure random bots do not join and spam your group you can enable a captcha option to have this done.
Now whenever a new member joins they would be made to provide an otp code for the verification and that will be used to authenticate the new member and allow them join the group. If the user fails to verify within a set time frame the authentication code will become invalid.

Captcha: {'✔ Enabled' if group['enable_captcha'] else '✖ Disabled'}
Expiry Duration: {group['unverified_user_duration']} Seconds
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def update_media_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')

    if re.match(r"^captcha-(\w+)", command).group(1) in ['true', 'false']:
        enable = False
        if re.match(r"^captcha-(\w+)", command).group(1) == 'true':
            enable = True
        LOGGER.info(enable)
        data = {"enable_captcha":enable}
    elif not re.match(r"^captcha-(.*?)", command).group(1) in ['true', 'false']:
        seconds = int(query.data[len("captcha-") :])
        LOGGER.info(seconds)
        data = {"unverified_user_duration":seconds}

    group = await update_group(group_id, data)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    captcha_button = InlineKeyboardButton(f"{'✔ Disable Captcha' if group['enable_captcha'] else '✖ Enable Captcha'}", callback_data=f"captcha-{'true' if not group['enable_captcha'] else 'false'}")
    captch_timestamp_button1 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 1 else ''} 1 Secs", callback_data="captcha-1")
    captch_timestamp_button2 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 2 else ''} 2 Secs", callback_data="captcha-2")
    captch_timestamp_button3 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 3 else ''} 3 Secs", callback_data="captcha-3")
    captch_timestamp_button4 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 4 else ''} 4 Secs", callback_data="captcha-4")
    captch_timestamp_button5 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 5 else ''} 5 Secs", callback_data="captcha-5")
    captch_timestamp_button6 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 6 else ''} 6 Secs", callback_data="captcha-6")
    captch_timestamp_button7 = InlineKeyboardButton(f"{'✔ ' if group['unverified_user_duration'] == 7 else ''} 7 Secs", callback_data="captcha-7")

    markup = [
        [captcha_button],
        [captch_timestamp_button1, captch_timestamp_button2, captch_timestamp_button3, captch_timestamp_button4, captch_timestamp_button5, captch_timestamp_button6, captch_timestamp_button7],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)


    message = f"""
<strong>Captcha Settings</strong>
To ensure random bots do not join and spam your group you can enable a captcha option to have this done.
Now whenever a new member joins they would be made to provide an otp code for the verification and that will be used to authenticate the new member and allow them join the group. If the user fails to verify within a set time frame the authentication code will become invalid.

Captcha: {'✔ Enabled' if group['enable_captcha'] else '✖ Disabled'}
Expiry Duration: {group['unverified_user_duration']} Seconds
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)








async def set_links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    group = await get_group(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    message_stack = get_message_stack(context)

    add_links_button = InlineKeyboardButton(f"Add Links", callback_data=f"links-add")
    links_button = InlineKeyboardButton(f"{'✖ Disable Link' if group['allow_links'] else '✔ Enable Link'}", callback_data=f"links-{'true' if not group['allow_links'] else 'false'}")

    markup = [
        [links_button],
        [add_links_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    words = await get_exception_links(group_id)
    banned_words = words['links']

    message = f"""
<strong>Links Settings</strong>
You can prevent links from being shown in your group from here

Links Watch: {'✔ Enabled' if group['allow_links'] else '✖ Disabled'}
Links Exception: {banned_words}.
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

SAVE_LINK_EXCEPTIONS = range(1)
async def open_link_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    match = re.match(r"^links-(\w+)", command)
    message_stack = get_message_stack(context)

    if match.group(1) == 'add':
        LOGGER.info("Adding Links")
        context.user_data['open_links_exception_message_id'] = message_id
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        context.user_data['bot_add_link_exception_message_id'] = await bot.send_message(chat_id=chat_id, text="Add link exceptions", reply_markup=ForceReply(selective=False, input_field_placeholder="Add Link Exceptions here"), parse_mode=ParseMode.HTML)
        return SAVE_LINK_EXCEPTIONS
    elif re.match(r"^links-(\w+)", command).group(1) in ['true', 'false']:
        LOGGER.info("Enabling or Disabling")
        enabled = True
        if re.match(r"^links-(\w+)", command).group(1) == "false":
            enabled = False
        data = {"allow_links":enabled}

        group = await update_group(group_id, data)


    group = await get_group(group_id)

    add_links_button = InlineKeyboardButton(f"Add Links", callback_data=f"links-add")
    links_button = InlineKeyboardButton(f"{'✖ Disable Link' if group['allow_links'] else '✔ Enable Link'}", callback_data=f"links-{'true' if not group['allow_links'] else 'false'}")

    markup = [
        [links_button],
        [add_links_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    words = await get_exception_links(group_id)
    banned_words = words['links']

    message = f"""
<strong>Links Settings</strong>
You can prevent links from being shown in your group from here

Links Watch: {'✔ Enabled' if group['allow_links'] else '✖ Disabled'}
Links Exception: {banned_words}.
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_link_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    link_message_id = context.user_data.get('open_links_exception_message_id')
    bot_message_id = context.user_data.get('bot_add_link_exception_message_id').message_id
    message_stack = get_message_stack(context)

    words = await update_exception_links(group_id, text)

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    group = await get_group(group_id)

    add_links_button = InlineKeyboardButton(f"Add Links", callback_data=f"links-add")
    links_button = InlineKeyboardButton(f"{'✖ Disable Link' if group['allow_links'] else '✔ Enable Link'}", callback_data=f"links-{'true' if not group['allow_links'] else 'false'}")

    markup = [
        [links_button],
        [add_links_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    banned_words = words['links']

    message = f"""
<strong>Links Settings</strong>
You can prevent links from being shown in your group from here

Links Watch: {'✔ Enabled' if group['allow_links'] else '✖ Disabled'}
Links Exception: {banned_words}.
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=bot_message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=link_message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)









SAVE_WELCOME_MESSAGE = range(1)
async def open_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    message_id = update.message.id if update.message else update.callback_query.message.id
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    message_stack = get_message_stack(context)

    group = await get_group(group_id)

    message = f"""
{'Add Welcome Message' if group['welcome_message'] is None else group['welcome_message']}
    """

    context.user_data['open_welcome_message_id'] = message_id
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    context.user_data['bot_update_welcome_message_id'] = await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Add a welcome message"), parse_mode=ParseMode.HTML)
    return SAVE_WELCOME_MESSAGE

async def update_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    message_id = update.message.id if update.message else update.callback_query.message.id
    group_id = context.user_data.get('selected_group')
    link_message_id = context.user_data.get('open_welcome_message_id')
    bot_message_id = context.user_data.get('bot_update_welcome_message_id').message_id
    message_stack = get_message_stack(context)
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id

    data = {"welcome_message": text}
    group = await update_group(group_id, data)


    message = f"""
{'Add Welcome Message' if group['welcome_message'] is None else group['welcome_message']}
    """

    markup = [
        [home_button],
        [permission_button, banned_button],
        [rules_button, spam_button],
        [captcha_button, warning_button],
        [media_button, tag_button],
        [link_button, check_button],
        [welcome_button, approval_button],
        [enable_buy_alert]
    ]


    keyboard = InlineKeyboardMarkup(markup)


    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=bot_message_id)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=link_message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)









async def set_spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    spam = await get_flood_settings(group_id)
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_stack = get_message_stack(context)

    seconds_button1 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 1 else ''}1 Sec(s)", callback_data="spam_seconds-1")
    seconds_button2 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 2 else ''}2 Sec(s)", callback_data="spam_seconds-2")
    seconds_button3 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 3 else ''}3 Sec(s)", callback_data="spam_seconds-3")
    seconds_button4 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 4 else ''}4 Sec(s)", callback_data="spam_seconds-4")
    seconds_button5 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 5 else ''}5 Sec(s)", callback_data="spam_seconds-5")

    messages_button1 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 1 else ''}1 Msg(s)", callback_data="spam_message-1")
    messages_button2 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 2 else ''}2 Msg(s)", callback_data="spam_message-2")
    messages_button3 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 3 else ''}3 Msg(s)", callback_data="spam_message-3")
    messages_button4 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 4 else ''}4 Msg(s)", callback_data="spam_message-4")
    messages_button5 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 5 else ''}5 Msg(s)", callback_data="spam_message-5")

    ban_button = InlineKeyboardButton(f"{'✔ ' if spam['ban'] else ''} Ban", callback_data=f"spam_ban-{'false' if spam['ban'] else 'true'}")
    kick_button = InlineKeyboardButton(f"{'✔ ' if spam['kick'] else ''} Kick", callback_data=f"spam_kick-{'false' if spam['kick'] else 'true'}")
    mute_button = InlineKeyboardButton(f"{'✔ ' if spam['mute'] else ''} Mute", callback_data=f"spam_mute-{'false' if spam['mute'] else 'true'}")

    markup = [
        [seconds_button1, seconds_button2, seconds_button3, seconds_button4, seconds_button5],
        [messages_button1, messages_button2, messages_button3, messages_button4, messages_button5],
        [ban_button, kick_button, mute_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Spam Settings</strong>

Messages to Send: {spam['messages_before_block']}
In Seconds: {spam['repeats_timeframe']}
ban: {'✔ ' if spam['ban'] else '✖'}
kick: {'✔ ' if spam['kick'] else '✖'}
mute: {'✔ ' if spam['mute'] else '✖'}

Works by setting the number of messages to send in a given second to prevent spamming
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)

async def update_spam_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    await query.answer()
    command = query.data
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_stack = get_message_stack(context)

    if re.match(r"^spam_seconds-(.*?)", command):
        seconds = int(query.data[len("spam_seconds-") :])
        data = {"repeats_timeframe":seconds}
    elif re.match(r"^spam_message-(.*?)", command):
        message = int(query.data[len("spam_message-") :])
        data = {"messages_before_block":message}
    elif re.match(r"^spam_kick-(\w+)", command):
        kick = False
        if re.match(r"^spam_kick-(\w+)", command).group(1) == 'true':
            kick = True
        data = {'kick': kick}
    elif re.match(r"^spam_ban-(\w+)", command):
        ban = False
        if re.match(r"^spam_ban-(\w+)", command).group(1) == 'true':
            ban = True
        data = {'ban': ban}
    elif re.match(r"^spam_mute-(\w+)", command):
        mute = False
        if re.match(r"^spam_mute-(\w+)", command).group(1) == 'true':
            mute = True
        data = {'mute': mute}

    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    group_id = context.user_data.get('selected_group')
    spam = await update_flood_settings(group_id, data)

    seconds_button1 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 1 else ''}1 Sec(s)", callback_data="spam_seconds-1")
    seconds_button2 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 2 else ''}2 Sec(s)", callback_data="spam_seconds-2")
    seconds_button3 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 3 else ''}3 Sec(s)", callback_data="spam_seconds-3")
    seconds_button4 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 4 else ''}4 Sec(s)", callback_data="spam_seconds-4")
    seconds_button5 = InlineKeyboardButton(f"{'✔ ' if spam['repeats_timeframe'] == 5 else ''}5 Sec(s)", callback_data="spam_seconds-5")

    messages_button1 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 1 else ''}1 Msg(s)", callback_data="spam_message-1")
    messages_button2 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 2 else ''}2 Msg(s)", callback_data="spam_message-2")
    messages_button3 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 3 else ''}3 Msg(s)", callback_data="spam_message-3")
    messages_button4 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 4 else ''}4 Msg(s)", callback_data="spam_message-4")
    messages_button5 = InlineKeyboardButton(f"{'✔ ' if spam['messages_before_block'] == 5 else ''}5 Msg(s)", callback_data="spam_message-5")

    ban_button = InlineKeyboardButton(f"{'✔ ' if spam['ban'] else ''} Ban", callback_data=f"spam_ban-{'false' if spam['ban'] else 'true'}")
    kick_button = InlineKeyboardButton(f"{'✔ ' if spam['kick'] else ''} Kick", callback_data=f"spam_kick-{'false' if spam['kick'] else 'true'}")
    mute_button = InlineKeyboardButton(f"{'✔ ' if spam['mute'] else ''} Mute", callback_data=f"spam_mute-{'false' if spam['mute'] else 'true'}")

    markup = [
        [seconds_button1, seconds_button2, seconds_button3, seconds_button4, seconds_button5],
        [messages_button1, messages_button2, messages_button3, messages_button4, messages_button5],
        [ban_button, kick_button, mute_button],
        [back_button],
    ]
    keyboard = InlineKeyboardMarkup(markup)

    message = f"""
<strong>Spam Settings</strong>

Messages to Send: {spam['messages_before_block']}
In Seconds: {spam['repeats_timeframe']}
ban: {'✔ ' if spam['ban'] else '✖'}
kick: {'✔ ' if spam['kick'] else '✖'}
mute: {'✔ ' if spam['mute'] else '✖'}

Works by setting the number of messages to send in a given second to prevent spamming
    """

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.edit_message_text(chat_id=chat_id, text=message, message_id=message_id, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # message_content = {"chat_id": chat_id, "message": message, "keyboard": keyboard, "message_id": message_id}
    # message_stack.append(message_content)



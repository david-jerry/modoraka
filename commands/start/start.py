import os
from pprint import pprint
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
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


from apps.users.datas import create_captcah, create_group, create_user, get_captcah, get_group, get_groups, get_user, get_user_by_username, update_group, update_user, update_user_group
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
permission_button = InlineKeyboardButton("🛡 Group Permissions 🛡", callback_data="permission_settings")
enable_buy_alert = InlineKeyboardButton("🟤 Enable Buy Alerts", callback_data="enable_buy_alert")
# enable_subscription = InlineKeyboardButton("🟤 Enable Subscription", callback_data="enable_subscription")
rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")

support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")
website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")


def formatted_button(user, subscription):
    markup = [
        [add_button],
        [trade_button],
        [support_button, website_button],
        # [enable_subscription],
        [enable_buy_alert],
        [settings_button, permission_button],
        [language_button]
    ]
    return markup

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
            keyboard = InlineKeyboardMarkup(
                markup
            )
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(chat_id=chat_id, text=help_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        if not user.username:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await context.bot.send_message(chat_id=chat_id, text="👮 Please I require a username setup in your profile account.")
            return None

        markup = [
            [home_button],
            [add_button],
            [trade_button],
            [support_button, website_button],
            [rules_button, help_button],
            [language_button]
        ]
        keyboard = InlineKeyboardMarkup(
            markup
        )
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=help_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=chat_id, text=help_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

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
            keyboard = InlineKeyboardMarkup(
                markup
            )
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(chat_id=chat_id, text=about_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        markup = [
            [home_button],
            [add_button],
            [trade_button],
            [support_button, website_button],
            [rules_button, help_button],
            [language_button]
        ]
        keyboard = InlineKeyboardMarkup(
            markup
        )
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=about_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=chat_id, text=about_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

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
            [back_button]
        ]

        keyboard = InlineKeyboardMarkup(
            markup
        )

        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Set a new language choice", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=chat_id, text="Set a new language choice", reply_markup=keyboard, parse_mode=ParseMode.HTML)

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

    language = query.data[len("choose_"):] #context.user_data.get('editing_group_chat_id')
    LOGGER.info(language)

    is_group = message_type in ("group", "supergroup", "channel")

    if not is_group:
        await update_user(user_id, {"chosen_language": language.title()})

        markup = [
            [add_button],
            [trade_button],
            [support_button, website_button],
            # [enable_subscription],
            [enable_buy_alert],
            [settings_button, permission_button],
            [language_button]
        ]
        keyboard = InlineKeyboardMarkup(
            markup
        )

        # Fetch the bot's profile photo
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"New language choice set to: <strong>{language.title()}</strong>", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=chat_id, text=f"New language choice set to: <strong>{language.title()}</strong>", reply_markup=keyboard, parse_mode=ParseMode.HTML)













async def ban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    bot = context.bot
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)

        group_data = await create_group({
            'chat_id': chat_id,
            'group_name': group_name,
            'about': about,
        })

    until_date = datetime.now() + timedelta(days=group_data['ban_duration'])

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
                await bot.send_message(chat_id=user_id, text="Invalid format. Please send <strong>/unban <user_id></strong>", parse_mode=ParseMode.HTML)
                return

            # Unban the user with the given ID
            # (Replace this with your actual unban code)
            await bot.ban_chat_member(chat_id=chat_id, user_id=user_data['user_id'], until_date=until_date, revoke_messages=True)

            # Send a confirmation message
            await bot.send_message(chat_id=chat_id, text=f"Banned user with ID: {user_data['username']}")
        else:
            await bot.send_message(chat_id=chat_id, text=f"🤠 I see what you are trying to do. Please contact an admin to assist with this.")

async def unban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    bot = context.bot
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)

        group_data = await create_group({
            'chat_id': chat_id,
            'group_name': group_name,
            'about': about,
        })

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
                await bot.send_message(chat_id=user_id, text="Invalid format. Please send <strong>/unban <user_id></strong>", parse_mode=ParseMode.HTML)
                return

            # Unban the user with the given ID
            # (Replace this with your actual unban code)
            await bot.unban_chat_member(chat_id=chat_id, user_id=user_data['user_id'])

            # Send a confirmation message
            await bot.send_message(chat_id=chat_id, text=f"Unbanned user with ID: {user_data['username']}")
        else:
            await bot.send_message(chat_id=chat_id, text=f"🤠 I see what you are trying to do. Please contact an admin to assist with this.")

async def on_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    user = update.message.new_chat_members[-1]

    # Access relevant information about the latest chat member
    user_id = user.id

    group = await get_group(chat_id)

    if group is None:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group = await create_group({
            'chat_id': chat_id,
            'group_name': group_name,
            'about': about,
        })


    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

    markup = [
        [support_button, website_button],
        [rules_button]
    ]

    keyboard = InlineKeyboardMarkup(
        markup
    )


    if update.message.new_chat_members:  # Check if new members joined
        # Check if the bot itself is among the new members
        if context.bot.id == user_id or context.bot.id in [member.id for member in update.message.new_chat_members]:

            # Perform actions assuming bot was added
            await  context.bot.send_message(chat_id=chat_id, text="Hi there! I'm excited to be part of this group. To set permissions and enable certain features please send a private message to me.", reply_markup=keyboard)

            private_button = InlineKeyboardButton("🤖 Chat with me 🤖", url="https://t.me/modoraka_bot")

            markup = [
                [private_button],
            ]
            keyboard = InlineKeyboardMarkup(
                markup
            )
            # Perform actions assuming bot was added
            await  context.bot.send_message(chat_id=chat_id, text="Send a message to me.", reply_markup=keyboard)
        else:
            expires = datetime.now() + timedelta(seconds=5)

            if not group['must_have_username']:
                user_data = await get_user(user_id=user_id)
                if user_data is None:
                    data = {
                        "name" : f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
                        "chat_id" : chat_id,
                        "user_id" : user_id,
                        "username" : user.username if user.username else user.user_id,
                        "subscribed" : False,
                        "violated" : False,
                        "chosen_language" : user.language_code,
                    }
                    user_data = await create_user(data)
            else:
                if not user.username:
                    await context.bot.send_message(chat_id=chat_id, text="Please we urge you to have a <strong>username</strong> filled to be a part of this group. Please NOTE: You have been removed until your username is setup.", parse_mode=ParseMode.HTML)
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=expires, revoke_messages=True)
                    return None

                user_data = await get_user(user_id=user_id)
                if user_data is None:
                    data = {
                        "name" : f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                        "chat_id" : chat_id,
                        "user_id" : user_id,
                        "username" : user.username if user.username else user.user_id,
                        "subscribed" : False,
                        "violated" : False,
                        "chosen_language" : "en",
                    }
                    user_data = await create_user(data)
                elif user.username != user_data['username']:
                    data = {
                        'username': user.username if user.username else user.user_id,
                    }
                    user_data = await update_user(user_id, data)


            if group['enable_captcha']:
                captcha_code = datetime.now() + timedelta(group['unverified_user_duration'])
                verify_captcha = InlineKeyboardButton(f"🗝 CODE: {captcha_code} 🗝", callback_data="verify_captcha")

                markup = [
                    [verify_captcha],
                ]

                keyboard = InlineKeyboardMarkup(
                    markup
                )

                user_captcha = await get_captcah(chat_id, user_id)
                if user_captcha is None or not user_captcha['used']:
                    await create_captcah(chat_id, user_id, int(captcha_code.timestamp()))
                    await context.bot.send_photo(chat_id=user_id, photo="https://www.shutterstock.com/image-illustration/3d-style-captcha-test-green-600nw-2308935989.jpg", caption=f"To complete your verification into the group you have to ensure the code in the button below corresponds to the code in the text below. If yes click on it to verify you are no robot.\n\nCODE: {captcha_code}", reply_markup=markup, parse_mode=ParseMode.HTML)
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=expires, revoke_messages=True)
                    return None


            welcome_message = group['welcome_message'] if group['welcome_message'] else "Hi there, You are welcome. Please take the time to read through the rules governing this group so as to prevent me from taking actions against you for violating them. Thank You!"
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
        await context.bot.send_message(chat_id=chat_id, text="👮 Please I require a username setup in your profile account.")
        return None

    user_data = await get_user(user_id=user_id)
    if user_data is None:
        data = {
        "name" : f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
        "chat_id" : chat_id,
        "user_id" : user_id,
        "username" : user.username if user.username else user.user_id,
        "subscribed" : False,
        "violated" : False,
        "chosen_language" : user.language_code,
        }
        user_data = await create_user(data)


    markup = await generate_button(command_name="start", user=user_data, is_group=is_group)
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    try:
        keyboard = InlineKeyboardMarkup(
            markup
        )
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=home_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except:
        await return_message(
            bot, chat_id, home_message, message_stack, message_id, False, False, None, markup
        )

async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_stack = get_message_stack(context)

    if len(message_stack) > 0:
        message = message_stack[-1]
        await context.bot.edit_message_text(
            text=message['message'],
            chat_id=message['chat_id'],
            message_id=message['message_id'],
            parse_mode=ParseMode.HTML,
            reply_markup=message['keyboard']
        )
        message_stack.pop()

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    context.user_data['editing_group_chat_id'] = chat_id

    # Fetch the bot's profile photo
    user_data = await get_user(user_id)
    if user_data is None:
        data = {
        "name" : f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
        "chat_id" : chat_id,
        "user_id" : user_id,
        "username" : user.username if user.username else user.user_id,
        "subscribed" : False,
        "violated" : False,
        "chosen_language" : user.language_code,
        }
        user_data = await create_user(data)

    if is_group:
        group_data = await get_group(chat_id)
        admins = await GroupBotActions.get_all_administrators(GroupBotActions, chat_id, bot)

        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        if group_data is None:
            group_data = await create_group({
                'chat_id': chat_id,
                'group_name': group_name,
                'about': about,
            })

        await update_user_group(user_id, chat_id)
        message = f"I am not aware of a predefined rule-set for this group. <strong>Please inform an admin to set this up for me.</strong>"
        rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
        delete_rules_button = InlineKeyboardButton("🚫 Delete Rules 🚫", callback_data=f"delete_rules-{chat_id}")
        support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")
        website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")

        set_rules_button = InlineKeyboardButton("✏ Set Rules ✏", callback_data=f"set_rules-{chat_id}")
        admin = await GroupBotActions.get_group_member(GroupBotActions, chat_id, user_id, bot)
        if group_data['about'] == ("" or None):
            markup = [
                [set_rules_button, delete_rules_button],
                [support_button, website_button]
            ]


            keyboard = InlineKeyboardMarkup(
                markup
            )

            markup_II = [
                [rules_button],
                [support_button, website_button]
            ]
            keyboard_II = InlineKeyboardMarkup(
                markup_II
            )

            if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
                if admin.status == ChatMemberStatus.OWNER:
                    await update_user_group(user_id, chat_id)
                # Perform actions assuming bot was added
                # message_stack = get_message_stack(context)
                # message_content = {"chat_id": chat_id, "message": message, "markup": markup, "message_id": message_id}
                await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
                await bot.send_message(chat_id=user_id, text=f"<strong>{group_name.title()}</strong>\n\nPlease add the regulations governing this group", reply_markup=keyboard, parse_mode=ParseMode.HTML)

            else:
                for ad in admins:
                    if not ad.user.is_bot:
                        await bot.send_chat_action(chat_id=ad.user.id, action=ChatAction.TYPING)
                        await bot.send_message(chat_id=ad.user.id, text=f"<strong>{group_name.title()}</strong>\n\nPlease add the regulations governing this group", reply_markup=keyboard, parse_mode=ParseMode.HTML)

                try:
                    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖🤖🤖🤖🤖\n\nI'm Sorry to break this to you, but we currently do not have a rule set. An admin has been alerted for this.", reply_markup=keyboard_II, parse_mode=ParseMode.HTML)
                except:
                    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                    await bot.send_message(chat_id=chat_id, text="🤖🤖🤖🤖🤖\n\nI'm Sorry to break this to you, but we currently do not have a rule set. An admin has been alerted for this.", reply_markup=keyboard_II, parse_mode=ParseMode.HTML)

        elif group_data is not None and group_data['about'] != ("" or None):
            message = group_data['about']
            markup = [
                [rules_button],
                [set_rules_button, delete_rules_button],
                [support_button, website_button],
            ]
            keyboard = InlineKeyboardMarkup(
                markup
            )

            markup_II = [
                [rules_button],
                [support_button, website_button]
            ]
            keyboard_II = InlineKeyboardMarkup(
                markup_II
            )


            # Perform actions assuming bot was added
            if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
                if admin.status == ChatMemberStatus.OWNER:
                    await update_user_group(user_id, chat_id)
                # Perform actions assuming bot was added
                # message_stack = get_message_stack(context)
                # message_content = {"chat_id": chat_id, "message": message, "markup": markup, "message_id": message_id}

                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard_II, parse_mode=ParseMode.HTML)
                await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                try:
                    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard_II, parse_mode=ParseMode.HTML)
                except:
                    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                    await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard_II, parse_mode=ParseMode.HTML)








RULES_EDIT_SAVE = range(1)
async def set_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    group_id = query.data[len("set_rules-"):] #context.user_data.get('editing_group_chat_id')
    context.user_data['editing_group_chat_id'] = group_id
    LOGGER.debug(f"Argument for Group ID: {group_id}")

    group_data = await get_group(group_id)

    if group_data is None:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group_data = await create_group({
            'chat_id': group_id,
            'group_name': group_name,
            'about': about,
        })

    admin = await GroupBotActions.get_group_member(GroupBotActions, group_id, user_id, bot)

    if not is_group:
        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)

            message = f"Please paste your rules in the input box."
            if group_data is not None and group_data['about'] != ("" or None):
                message = group_data['about']

            # Perform actions assuming bot was added
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.send_message(chat_id=chat_id, text=message, reply_markup=ForceReply(selective=False, input_field_placeholder="Type or Paste your rules here."), parse_mode=ParseMode.HTML)
            return RULES_EDIT_SAVE
        else:
            ConversationHandler.END
            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [
                [support_button, website_button],
                [rules_button]
            ]
            keyboard = InlineKeyboardMarkup(
                markup
            )
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="You are not an admin in this group. Nice try mate! 😂", reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def save_set_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    text = update.message.text if update.message else update.callback_query.message.text
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id



    group_id = context.user_data.get('editing_group_chat_id')
    LOGGER.debug(f"Save Rules Group ID: {group_id}")

    data = {
        "about": text
    }
    LOGGER.debug(text)

    group_data = await update_group(group_id, data)

    user_data = await get_user(user_id=user_id)
    if user_data is None:
        data = {
            "name" : f"{user.first_name} {user.last_name}" if user.first_name or user.username else user.user_id,
            "chat_id" : chat_id,
            "user_id" : user_id,
            "username" : user.username if user.username else user.user_id,
            "subscribed" : False,
            "violated" : False,
            "chosen_language" : user.language_code,
        }
        user_data = await create_user(data)

    message = group_data['about']

    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

    markup = [
        [rules_button, website_button],
        [support_button]
    ]
    keyboard = InlineKeyboardMarkup(
        markup
    )

    await bot.send_chat_action(chat_id=group_id, action=ChatAction.TYPING)
    await bot.send_message(chat_id=group_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    ConversationHandler.END

async def delete_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    query.answer()

    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    message_stack = get_message_stack(context)
    is_group = message_type in ("group", "supergroup", "channel")

    group_id = query.data[len("delete_rules-"):] #context.user_data.get('editing_group_chat_id')

    admin = await GroupBotActions.get_group_member(GroupBotActions, group_id, user_id, bot)

    if not is_group:
        user_data = await get_user(user_id)

        if admin.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            if admin.status == ChatMemberStatus.OWNER:
                await update_user_group(user_id, chat_id)

            data = {
                "about": None
            }

            await update_group(group_id, data)

            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [
                [rules_button, website_button],
                [support_button]
            ]
            keyboard = InlineKeyboardMarkup(
                markup
            )

            # Perform actions assuming bot was added
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await  context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Your bot's rules has been removed", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")

            markup = [
                [rules_button, website_button],
                [support_button]
            ]
            keyboard = InlineKeyboardMarkup(
                markup
            )
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await  bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="You are not an admin in this group. Nice try mate! 😂", reply_markup=keyboard, parse_mode=ParseMode.HTML)







async def intervention_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message = update.message if update.message else update.callback_query.message
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
    is_group = message_type in ("group", "supergroup", "channel")

    group_data = await get_group(chat_id)

    if group_data is None:
        group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
        about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
        group_data = await create_group({
            'chat_id': chat_id,
            'group_name': group_name,
            'about': about,
        })

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
                await bot.send_message(chat_id=admin_data['user_id'], text=f"<code>FROM: {group_name.title()}</code>\n\nPlease respond to @{user_data['username'] if user_data['username'] else update.message.from_user.username}. He/She has a reason for you to intevene.", parse_mode=ParseMode.HTML)
                # Send a confirmation message
                await bot.send_message(chat_id=chat_id, text=f"@{admin_data['username'].title()}\n\nWould respond to you immeditely they get you message.", parse_mode=ParseMode.HTML)
            except Exception as e:
                LOGGER.info(e)
                for ad in admins:
                    user_data = await get_user(user_id)
                    if not ad.user.is_bot:
                        await bot.send_message(chat_id=ad.user.id, text=f"<code>FROM: {group_name.title()}</code>\n\nPlease respond to @{user_data['username']}. He/She has a reason for you to intevene.", parse_mode=ParseMode.HTML)
                # Send a confirmation message
                await bot.send_message(chat_id=chat_id, text=f"@{user_data['username'] if user_data['username'] else update.message.from_user.username} An admin would respond to you privately.", parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id=chat_id, text=f"🤠 you are already an admin. What would you like to do?")





# async def enable_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     bot = context.bot
#     chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
#     message = update.message if update.message else update.callback_query.message
#     message_id = message.message_id
#     user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
#     message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type
#     is_group = message_type in ("group", "supergroup", "channel")

#     # tiers = await get_subscription_tiers()

#     if not is_group:
#         markup = [
#             [home_button],
#             [add_button],
#             # [trade_button],
#             # [support_button, website_button],
#         ]
#         # for tier in tiers:
#         #     markup.append([InlineKeyboardButton(f"{tier['name'].title()} - {tier['price']} USDT", callback_data=f"group_{tier['id']}")])

#         # Build the reply markup
#         keyboard = InlineKeyboardMarkup(markup)

#         try:
#             await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
#             await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Select a tier to subscribe to", reply_markup=keyboard, parse_mode=ParseMode.HTML)
#         except:
#             await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
#             await bot.delete_message(chat_id=chat_id, message_id=message_id)
#             await bot.send_message(chat_id=chat_id, text="Select a tier to subscribe to", reply_markup=keyboard, parse_mode=ParseMode.HTML)


# async def choose_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     bot = context.bot
#     user = update.message.from_user if update.message else update.callback_query.from_user
#     user_id = user.id
#     chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
#     message_id = update.message.id if update.message else update.callback_query.message.id
#     message_type = update.message.chat.type if update.message else update.callback_query.message.chat.type

#     sub_id = query.data[len("choose_"):] #context.user_data.get('editing_group_chat_id')
#     LOGGER.info(sub_id)

#     is_group = message_type in ("group", "supergroup", "channel")

#     # sub = await get_subscription_tier(sub_id)

#     if not is_group:
#         groups = await get_groups(user_id)

#         markup = [
#             [back_button],
#         ]

#         for group in groups:
#             markup.append([InlineKeyboardButton(f"{'💚' if group['subscribed'] else '💓'} {group['group_name'].title()}", callback_data=f"group_{group['chat_id']}")])

#         keyboard = InlineKeyboardMarkup(
#             markup
#         )

#         # Fetch the bot's profile photo
#         await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
#         try:
#             await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Select {sub['features']}", reply_markup=keyboard, parse_mode=ParseMode.HTML)
#         except:
#             await bot.send_message(chat_id=chat_id, text=f"New language choice set to: <strong>{language.title()}</strong>", reply_markup=keyboard, parse_mode=ParseMode.HTML)



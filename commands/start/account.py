import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, helpers
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    CallbackContext,
    ConversationHandler,
)
from commands.start.buttons import keyboard_from_buttons

from utils.logger import LOGGER
from utils.utils import get_about_text, get_bot_photo, get_message_stack, return_message


from apps.users.datas import create_user, get_group, get_user, update_user

async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.effective_chat.id
    user = update.message.from_user
    user_id = user.id
    message_type = update.message.chat.type

    group_data = await get_group(chat_id)

    awaited_data = await get_user(user_id)
    member_id = awaited_data['id'] if awaited_data is not None else 0


    status = awaited_data["subscribed"] if awaited_data is not None else False
    LOGGER.debug(status)

    if status:
        subed_account = "subscribed_account"
    else:
        subed_account = "unsubscribed_account"

    message_stack = get_message_stack(context)

    # Fetch the bot's profile photo
    photo = None
    text_message = f"""
------------------------------------------------------
<strong>{awaited_data['username'].upper() if awaited_data['username'] else awaited_data['chat_id']} Account Details</strong>
------------------------------------------------------

<strong>NAME</strong> ---------------- <code>{awaited_data['name']}</code>
<strong>PHONE</strong> ---------------- <code>{awaited_data['phone']}</code>
<strong>USERNAME</strong> ---------------- <code>{awaited_data['username']}</code>
<strong>LANGUAGE CHOICE</strong> ---------------- <code>{awaited_data['chosen_language']}</code>
<strong>SUBSCRIBED</strong> ---------------- <code>{awaited_data['subscribed']}</code>
<strong>VIOLATED RULES</strong> ---------------- <code>{awaited_data['violated']}</code>
<strong>AGREED TO TERMS</strong> ---------------- <code>{awaited_data['agreed_to_terms']}</code>
    """ if awaited_data is not None else "Create an account by starting a conversation directly with @modoraka"

    if group_data != None and message_type == 'supergroup':
        language_markup = keyboard_from_buttons(state=subed_account)  if group_data['admin_id'] == member_id else []
    else:
        language_markup = keyboard_from_buttons(state=subed_account)

    not_admin_message = "You have to be subscribed as a user or be the admin to view your account details." if group_data['admin_id'] != member_id else text_message

    await return_message(False, bot, chat_id, photo, not_admin_message, message_stack, True, language_markup)

ANSWER = range(1)
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.effective_chat.id
    user = update.message.from_user
    user_id = user.id
    message_type = update.message.chat.type

    group_data = await get_group(chat_id)

    awaited_data = await get_user(user_id)
    member_id = awaited_data['id'] if awaited_data is not None else 0


    status = awaited_data["subscribed"] if awaited_data is not None else False
    LOGGER.debug(status)

    if status:
        subed_account = "subscribed_account"
    else:
        subed_account = "unsubscribed_account"

    message_stack = get_message_stack(context)

    # Fetch the bot's profile photo
    photo = None
    text_message = f"""
------------------------------------------------------
<strong>Update {awaited_data['username'].upper() if awaited_data['username'] else awaited_data['chat_id']} Account Details</strong>
------------------------------------------------------

Update Your information by adopting the example format below.

    """ + """
eg: <pre>{
    'name': 'John Doe',
    'username': 'jndoe',
    'phone': '+1234567890'
}</pre>
    """

    await return_message(True, bot, user_id, photo, text_message, message_stack, True, markup)
    return ANSWER

async def update_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.effective_chat.id
    user = update.message.from_user
    user_id = user.id
    message_type = update.message.chat.type

    group_data = await get_group(chat_id)

    awaited_data = await get_user(user_id)
    member_id = awaited_data['id'] if awaited_data is not None else 0


    status = awaited_data["subscribed"] if awaited_data is not None else False
    LOGGER.debug(status)

    if status:
        subed_account = "subscribed_account"
    else:
        subed_account = "unsubscribed_account"

    message_stack = get_message_stack(context)

    # Fetch the bot's profile photo
    photo = None
    text_message = f"""
------------------------------------------------------
<strong>Premium Subscribtion</strong>
------------------------------------------------------

Choose One of the plans and subscribe to.

    """ if awaited_data is not None else "Create an account by starting a conversation directly with @modoraka"

    if group_data != None and message_type == 'supergroup':
        language_markup = keyboard_from_buttons(state=subed_account)  if group_data['admin_id'] == member_id else []
    else:
        language_markup = keyboard_from_buttons(state=subed_account)

    not_admin_message = "You have to be subscribed as a user or be the admin to update your account details." if group_data['admin_id'] != member_id else text_message

    await return_message(False, bot, chat_id, photo, not_admin_message, message_stack, True, language_markup)

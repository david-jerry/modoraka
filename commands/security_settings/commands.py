from telegram import MessageEntity, Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.warnings import PTBUserWarning
from telegram.constants import ParseMode
from apps.users.datas import add_group_offenders, create_group, get_group
from utils.check_profanity import profanity_check

from utils.logger import LOGGER
from utils.utils import GroupBotActions, GroupBotFilters


async def check_for_profanity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text
    chat_id = message.chat.id
    chat_type = message.chat.type
    message_id = message.message_id

    if chat_type in ("supergroup", "group", "channel"):
        is_abusive = await profanity_check(text)
        group = await get_group(chat_id)
        if group is None:
            group_name = await GroupBotActions.get_group_name(bot=context.bot, chat_id=chat_id)
            about = await GroupBotActions.get_group_about(bot=context.bot, chat_id=chat_id)
            group = await create_group(
                {
                    "chat_id": chat_id,
                    "group_name": group_name,
                    "about": about,
                }
            )
        if is_abusive:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text="""
    Please try to be respectful when addressing others. We do not condone any form of abuse in this group.
                """,
            )


async def check_message_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # --------------------------------------------------------------------
    # TODO: A data function to store the amount of words to allow in a group text message
    # --------------------------------------------------------------------
    message = update.message.text
    chat_id = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type in ("supergroup", "group", "channel"):
        group = await get_group(chat_id)
        if group is None:
            group_name = await GroupBotActions.get_group_name(bot=context.bot, chat_id=chat_id)
            about = await GroupBotActions.get_group_about(bot=context.bot, chat_id=chat_id)
            group = await create_group(
                {
                    "chat_id": chat_id,
                    "group_name": group_name,
                    "about": about,
                }
            )

        max_length = group["max_message_length"] if group is not None else 300  # Adjust the maximum allowed length

        if (
            group["watch_length"]
            and len(message) > max_length
            and (chat_type == "supergroup" or chat_type == "group" or chat_type == "channel")
        ):
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text="""
    Please try to keep your messages short and concise. Messages longer than {} characters can be overwhelming. Consider breaking it down into smaller parts.
                """.format(
                    max_length
                ),
            )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user if update.message else update.callback_query.from_user
    chat_id = update.effective_chat.id if update.message else update.callback_query.message.chat.id
    message_id = update.message.id if update.message else update.callback_query.message.id
    context.user_data.clear()
    LOGGER.debug(f"{user.username if user.username else user.id} Has Canceled the conversation")
    cancel_message = "Alright Mate! I hope we can continue from where we left off."
    await context.bot.delete_message(chat_id, message_id)
    await context.bot.send_message(chat_id, cancel_message, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def check_message_contains_bot_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    user_id = user.id
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type in ("supergroup", "group", "channel"):
        group = await get_group(chat_id)
        if group is None:
            group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
            about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
            group = await create_group(
                {
                    "chat_id": chat_id,
                    "group_name": group_name,
                    "about": about,
                }
            )

        if (
            group is not None
            and group["watch_for_spam"]
            and GroupBotFilters.bot_usernames_exist_filter(GroupBotFilters, message)
            and (chat_type == "supergroup" or chat_type == "group" or chat_type == "channel")
        ):
            # --------------------------------------------------------------------
            # TODO: A data function to store the offending user incase they repeat
            # the action then it should completely remove or ban them
            # --------------------------------------------------------------------
            group = await add_group_offenders(chat_id, user_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=message.id)
            if user_id in group["offenders"]:
                await GroupBotActions.ban_chat_member(
                    GroupBotActions,
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=context.bot,
                    ban_duration_in_days=group["ban_duration"],
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"""
        ⚠ <code>{user.username.upper() if user.username else user.id}<code> ⚠

        Please be warned. We do not entertain posting bot links here. if repeated we shall ban you from this group.
                    """,
                    parse_mode=ParseMode.HTML,
                )


async def check_message_contains_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    user_id = user.id
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type in ("supergroup", "group", "channel"):
        group = get_group(chat_id)
        if group is None:
            group_name = await GroupBotActions.get_group_name(GroupBotActions, bot=context.bot, chat_id=chat_id)
            about = await GroupBotActions.get_group_about(GroupBotActions, bot=context.bot, chat_id=chat_id)
            group = await create_group(
                {
                    "chat_id": chat_id,
                    "group_name": group_name,
                    "about": about,
                }
            )

        if (
            group is not None
            and not group["allow_links"]
            and GroupBotFilters.links_exist_filter(GroupBotFilters, message)
            and (chat_type == "supergroup" or chat_type == "group" or chat_type == "channel")
        ):
            # --------------------------------------------------------------------
            # TODO: A data function to store the offending user incase they repeat
            # the action then it should completely remove or ban them
            # --------------------------------------------------------------------
            group = await add_group_offenders(chat_id, user_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=message.id)
            if user_id in group["offenders"]:
                await GroupBotActions.ban_chat_member(
                    GroupBotActions,
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=context.bot,
                    ban_duration_in_days=group["ban_duration"],
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"""
        ⚠ <code>{user.username.upper() if user.username else user.id}<code> ⚠

        Please be warned. We do not allow links here.
                    """,
                    parse_mode=ParseMode.HTML,
                )

from pprint import pprint
import re
from warnings import filterwarnings
from telegram import Update
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
from apps.users.datas import (
    add_group_offenders,
    add_media_actions,
    create_group,
    create_user,
    get_banned_words,
    get_group,
    get_user,
)
from commands.errors.commands import error_handler, log_error
from commands.security_settings.commands import (
    cancel_command,
)
from commands.start.start import (
    about_command,
    back_command,
    ban_user_command,
    choose_language_command,
    delete_rules_command,
    # enable_subscription_command,
    help_command,
    intervention_command,
    language_command,
    on_new_members,
    open_link_settings,
    open_welcome_message,
    rules_command,
    save_details_settings,
    save_set_rules_command,
    save_token_settings,
    set_address_command,
    set_captcha_command,
    set_check_command,
    set_detail_command,
    set_links_command,
    set_rules_command,
    set_spam_command,
    set_tagging_command,
    set_warning_command,
    start_command,
    unban_user_command,
    choose_group,
    set_selected_group,
    set_banned_words_command,
    save_banned_words_command,
    update_captcha_settings,
    update_check_settings,
    update_details_settings,
    update_link_settings,
    update_mention_settings,
    update_spam_settings,
    update_tagging_settings,
    update_token_settings,
    update_warning_settings,
    update_warnings_para_settings,
    update_warnings_settings,
    update_welcome_message,
)
from utils.check_profanity import profanity_check, translate_text
from utils.env_result import DEVELOPER_ID, TOKEN, USERNAME

from utils.logger import LOGGER
from utils.utils import GroupBotActions, GroupBotFilters

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from utils.constants import help_message


async def handle_response(text: str, language_code: str = "EN") -> str:
    processed_text = text.lower()
    # Call the OpenAI API to get a response

    return translate_text(processed_text, language_code)


async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    message = update.message
    user_id = update.message.from_user.id  # to determin the chat type private or group
    CHAT_ID = update.message.chat.id
    chat_id = CHAT_ID
    text: str = update.message.text  # messgae that will be processed
    message_id = update.message.message_id

    LOGGER.info(pprint(update.message))

    LOGGER.debug(f"user: {update.message.chat.id} in {message_type}: '{text}'")

    # --------------------------------------------------------------------
    # TODO: A data function to retreive the user's saved language choice
    # --------------------------------------------------------------------

    media_action = await add_media_actions(chat_id)

    LOGGER.info(f"text is not none: {text is not None}")

    if message_type in ("group", "supergroup", "channel"):
        # check for media uploads
        if media_action is None:
            media_action = await add_media_actions(chat_id)

        medias = {
            "images": media_action["images"],
            "videos": media_action["videos"],
            "animation": media_action["animation"],
            "audio": media_action["audio"],
            "sticker": media_action["sticker"],
            "documents": media_action["documents"],
        }

        # check for media uploads and their functions
        if (
            message.media_group_id
            or message.photo
            or message.video
            or message.animation
            or message.document
            or message.sticker
        ):
            LOGGER.info(medias.items())
            if all(action in {1, 2, 3, 4} for action in medias.values()):
                group = await add_group_offenders(chat_id, user_id)
                # Perform actions based on media_action values
                for media_type, action in medias.items():
                    if action == 1 and media_type in (
                        "images",
                        "videos",
                        "animation",
                        "audio",
                        "sticker",
                        "documents",
                    ):
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="""
    Please We do not allow such media types here
                            """,
                        )
                    elif action == 2 and media_type in (
                        "images",
                        "videos",
                        "animation",
                        "audio",
                        "sticker",
                        "documents",
                    ):
                        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                    elif action == 3 and media_type in (
                        "images",
                        "videos",
                        "animation",
                        "audio",
                        "sticker",
                        "documents",
                    ):
                        if user_id in group["offenders"]:
                            await GroupBotActions.ban_chat_member(
                                GroupBotActions,
                                user_id=user_id,
                                chat_id=chat_id,
                                bot=context.bot,
                                ban_duration_in_days=group["ban_duration"],
                            )
                    elif action == 4 and media_type in (
                        "images",
                        "videos",
                        "animation",
                        "audio",
                        "sticker",
                        "documents",
                    ):
                        # Delete and Ban or take appropriate action for media_type "audio", "documents", etc.
                        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                        if user_id in group["offenders"]:
                            await GroupBotActions.ban_chat_member(
                                GroupBotActions,
                                user_id=user_id,
                                chat_id=chat_id,
                                bot=context.bot,
                                ban_duration_in_days=group["ban_duration"],
                            )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    message = update.message
    user_id = update.message.from_user.id  # to determin the chat type private or group
    CHAT_ID = update.message.chat.id
    chat_id = CHAT_ID
    text: str = update.message.text  # messgae that will be processed
    message_id = update.message.message_id

    LOGGER.info(pprint(update.message))

    LOGGER.debug(f"user: {update.message.chat.id} in {message_type}: '{text}'")

    # --------------------------------------------------------------------
    # TODO: A data function to retreive the user's saved language choice
    # --------------------------------------------------------------------

    language_code = update.message.from_user.language_code

    LOGGER.info(f"text is not none: {text is not None}")

    if message_type == "private":
        user = update.message.from_user
        user_id = user.id
        user = await get_user(user_id=user_id)
        if user is None:
            data = {
                "name": f"{user.first_name} {user.last_name}" if user.first_name or user.username else "",
                "chat_id": CHAT_ID,
                "user_id": user_id,
                "subscribed": False,
                "violated": False,
                "chosen_language": language_code,
            }
            user = await create_user(data)

        response: str = await handle_response(text, user["chosen_language"])
        await context.bot.send_message(chat_id=user_id, text=response, parse_mode=ParseMode.HTML)
        return None
    elif message_type in ("group", "supergroup", "channel") and USERNAME in text:
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
        new_text: str = (
            f"<strong>{USERNAME} Says</strong>: How may I assist you? Perhaps you intend to connect with me directly, then use this link below: https://t.me/modoraka_bot"  # text.replace(USERNAME, "").strip()
        )
        response: str = await handle_response(new_text)
        words = await get_banned_words(chat_id)

        LOGGER.info(words)

        if response in words:
            await context.bot.send_message(
                chat_id=CHAT_ID, text="Violation of unacceptable word used. Please refrain.", parse_mode=ParseMode.HTML
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            await GroupBotActions.ban_chat_member(
                GroupBotActions,
                chat_id=CHAT_ID,
                user_id=user_id,
                bot=context.bot,
                ban_duration_in_days=group["ban_duration"],
            )
        await context.bot.send_message(chat_id=CHAT_ID, text=response, parse_mode=ParseMode.HTML)

    elif message_type in ("group", "supergroup", "channel"):
        new_text: str = text
        response: str = await handle_response(new_text)

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

        words = await get_banned_words(chat_id)
        LOGGER.info(words)

        if response in words:
            await context.bot.send_message(
                chat_id=CHAT_ID, text="Violation of unacceptable word used. Please refrain.", parse_mode=ParseMode.HTML
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            await GroupBotActions.ban_chat_member(
                GroupBotActions,
                chat_id=CHAT_ID,
                user_id=user_id,
                bot=context.bot,
                ban_duration_in_days=group["ban_duration"],
            )
            return None

        # handle hash tg use
        LOGGER.info(group["allow_hash"])
        LOGGER.info(re.search(r"#\w+", response))
        # Prevent the user from using hashtags
        if re.search(r"#\w+", response) and not group["allow_hash"]:
            await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            await context.bot.send_message(chat_id=chat_id, text="Sorry, using hashtags is not allowed in this group.")
            return None

        # Handle Profanity Check Here
        is_abusive = profanity_check(response)
        if is_abusive:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text="""
    Please try to be respectful when addressing others. We do not condone any form of abuse in this group.
                """,
            )
            return None

        # watch for lengthy messages
        max_length = group["max_message_length"] if group is not None else 300  # Adjust the maximum allowed length

        if group["watch_length"] and len(response) > max_length:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text="""
    Please try to keep your messages short and concise. Messages longer than {} characters can be overwhelming. Consider breaking it down into smaller parts.
                """.format(
                    max_length
                ),
            )
            return None

        # Check if text contains username or bot name
        if (
            group is not None
            and group["watch_for_spam"]
            and GroupBotFilters.bot_usernames_exist_filter(GroupBotFilters, update.message, CHAT_ID)
        ):
            # --------------------------------------------------------------------
            # TODO: A data function to store the offending user incase they repeat
            # the action then it should completely remove or ban them
            # --------------------------------------------------------------------
            group = await add_group_offenders(chat_id, user_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            if user_id in group["offenders"]:
                await GroupBotActions.ban_chat_member(
                    GroupBotActions,
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=context.bot,
                    ban_duration_in_days=group["ban_duration"],
                )
                return None
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"""
        ⚠ <code>{user.username.upper() if user.username else user.id}<code> ⚠

        Please be warned. We do not entertain posting bot links here. if repeated we shall ban you from this group.
                    """,
                    parse_mode=ParseMode.HTML,
                )
                return None

        # check if text contains links
        if (
            group is not None
            and not group["allow_links"] and not group['allow_tagging']
            and GroupBotFilters.links_exist_filter(GroupBotFilters, update.message, CHAT_ID)
        ):
            # --------------------------------------------------------------------
            # TODO: A data function to store the offending user incase they repeat
            # the action then it should completely remove or ban them
            # --------------------------------------------------------------------
            group = await add_group_offenders(chat_id, user_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            if user_id in group["offenders"]:
                await GroupBotActions.ban_chat_member(
                    GroupBotActions,
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=context.bot,
                    ban_duration_in_days=group["ban_duration"],
                )
                return None
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"""
        ⚠ <code>{user.username.upper() if user.username else user.id}<code> ⚠

        Please be warned. We do not allow links here.
                    """,
                    parse_mode=ParseMode.HTML,
                )
                return None


def main() -> None:
    LOGGER.info(USERNAME)
    LOGGER.info(DEVELOPER_ID)
    LOGGER.info("Starting the Modoraka Bot")
    app = Application.builder().token(TOKEN).build()
    LOGGER.info("App initialized")
    LOGGER.info("Commands are Ready")

    RULES_EDIT_SAVE = range(1)
    rules_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                set_rules_command,
                pattern=r"^set_rules-",
            )
        ],
        states={RULES_EDIT_SAVE: [MessageHandler(filters.TEXT & ~(filters.COMMAND), save_set_rules_command)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(rules_conversation)




    SAVE_BANNED_WORDS = range(1)
    banned_words_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                set_banned_words_command,
                pattern=r"^banned_words$",
            )
        ],
        states={SAVE_BANNED_WORDS: [MessageHandler(filters.TEXT & ~(filters.COMMAND), save_banned_words_command)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(banned_words_conversation)




    SAVE_WELCOME_MESSAGE = range(1)
    welcome_message_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                open_welcome_message,
                pattern=r"^welcome$",
            )
        ],
        states={SAVE_WELCOME_MESSAGE: [MessageHandler(filters.TEXT & ~(filters.COMMAND), update_welcome_message)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(welcome_message_conversation)


    DETAIL_SETTING = range(1)
    detail_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                update_details_settings,
                pattern=r"^warnings-",
            )
        ],
        states={DETAIL_SETTING: [MessageHandler(filters.TEXT & ~(filters.COMMAND), save_details_settings)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(detail_conversation)




    TOKEN_SETTING = range(1)
    token_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                update_token_settings,
                pattern=r"^symbol$",
            )
        ],
        states={TOKEN_SETTING: [MessageHandler(filters.TEXT & ~(filters.COMMAND), save_token_settings)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(token_conversation)






    WARNING_SETTING = range(1)
    mute_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                update_warnings_settings,
                pattern=r"^warnings-",
            )
        ],
        states={WARNING_SETTING: [MessageHandler(filters.TEXT & ~(filters.COMMAND), update_warnings_para_settings)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(mute_conversation)





    SAVE_LINK_EXCEPTIONS = range(1)
    links_exception_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                open_link_settings,
                pattern=r"^links-add$",
            )
        ],
        states={SAVE_LINK_EXCEPTIONS: [MessageHandler(filters.TEXT & ~(filters.COMMAND), update_link_settings)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(links_exception_conversation)

    app.add_handler(MessageHandler(filters.Regex(r"^Back ↩"), back_command))

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("unban", unban_user_command))
    app.add_handler(CommandHandler("ban", ban_user_command))
    app.add_handler(CommandHandler("intervene", intervention_command))
    app.add_handler(CommandHandler("rules", rules_command))

    app.add_handler(CallbackQueryHandler(set_address_command, pattern=r"^enable_buy_alert$"))

    app.add_handler(CallbackQueryHandler(start_command, pattern=r"^home$"))
    app.add_handler(CallbackQueryHandler(choose_group, pattern=r"^bot_settings$"))
    app.add_handler(CallbackQueryHandler(set_selected_group, pattern=r"^group-"))
    app.add_handler(CallbackQueryHandler(back_command, pattern=r"^back$"))
    app.add_handler(CallbackQueryHandler(cancel_command, pattern=r"^cancel$"))

    app.add_handler(CallbackQueryHandler(help_command, pattern=r"^help$"))
    app.add_handler(CallbackQueryHandler(language_command, pattern=r"^choose_language$"))
    app.add_handler(CallbackQueryHandler(rules_command, pattern=r"^rules$"))
    app.add_handler(CallbackQueryHandler(choose_language_command, pattern=r"^choose_"))
    app.add_handler(CallbackQueryHandler(delete_rules_command, pattern=r"^delete_rules-"))

    app.add_handler(CallbackQueryHandler(set_links_command, pattern=r"^links$"))
    app.add_handler(CallbackQueryHandler(open_link_settings, pattern=r"^links-"))

    app.add_handler(CallbackQueryHandler(set_check_command, pattern=r"^checks$"))
    app.add_handler(CallbackQueryHandler(update_check_settings, pattern=r"^checks_username-"))
    app.add_handler(CallbackQueryHandler(update_check_settings, pattern=r"^checks_about-"))
    app.add_handler(CallbackQueryHandler(update_check_settings, pattern=r"^checks_description-"))

    app.add_handler(CallbackQueryHandler(set_detail_command, pattern=r"^detail$"))



    app.add_handler(CallbackQueryHandler(set_warning_command, pattern=r"^warning$"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-1$"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-2$"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-3$"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-4$"))
    app.add_handler(CallbackQueryHandler(update_warning_settings, pattern=r"^warning-5$"))

    app.add_handler(CallbackQueryHandler(set_tagging_command, pattern=r"^tag$"))
    app.add_handler(CallbackQueryHandler(update_tagging_settings, pattern=r"^tagging-"))
    app.add_handler(CallbackQueryHandler(update_mention_settings, pattern=r"^mention-"))

    app.add_handler(CallbackQueryHandler(set_spam_command, pattern=r"^spam$"))
    app.add_handler(CallbackQueryHandler(update_spam_settings, pattern=r"^spam_seconds-"))
    app.add_handler(CallbackQueryHandler(update_spam_settings, pattern=r"^spam_message-"))
    app.add_handler(CallbackQueryHandler(update_spam_settings, pattern=r"^spam_ban-"))
    app.add_handler(CallbackQueryHandler(update_spam_settings, pattern=r"^spam_kick-"))
    app.add_handler(CallbackQueryHandler(update_spam_settings, pattern=r"^spam_mute-"))

    app.add_handler(CallbackQueryHandler(set_captcha_command, pattern=r"^captcha$"))
    app.add_handler(CallbackQueryHandler(update_captcha_settings, pattern=r"^captcha-"))

    # Cancel Any conversation handler
    app.add_handler(CommandHandler("cancel", cancel_command))

    # handle messages
    LOGGER.info("Message handler initiated")
    app.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_members))
    app.add_handler(
        MessageHandler(filters.ANIMATION | filters.AUDIO | filters.PHOTO | filters.ATTACHMENT, handle_media_message)
    )

    # error commands
    app.add_error_handler(log_error)
    app.add_error_handler(error_handler)

    LOGGER.info("Hit Ctrl + C to terminate the server")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

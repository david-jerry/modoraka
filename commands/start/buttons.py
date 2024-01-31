from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters, CallbackContext

from utils.env_result import ADMINCHATID



async def generate_button(command_name="start", user=None, is_group=False, group=None):
    home_button = InlineKeyboardButton("🏠 Home 🏠", callback_data="return_home")
    rules_button = InlineKeyboardButton("📘 Rules 📘", callback_data="rules")
    previous_button = InlineKeyboardButton("⏪ Previous", callback_data="previous")
    next_button = InlineKeyboardButton("Next ⏩", callback_data="next")
    groups_button = InlineKeyboardButton("🙌 My Groups 🙌", callback_data="groups")


    commands_button = InlineKeyboardButton("⛓ Commands ⛓", callback_data="commands")
    basic_commands_button = InlineKeyboardButton("⛓ Basic Commands ⛓", callback_data="basic_commands")
    pro_commands_button = InlineKeyboardButton("⛓ Pro Commands ⛓", callback_data="pro_commands")

    add_button = InlineKeyboardButton("➕ Add Modoraka to Group ➕", url="https://t.me/modoraka_bot?startgroup=start")
    trade_button = InlineKeyboardButton("🎯 Add TradoRaka to Group 🎯", url="https://t.me/modoraka_bot")
    website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url="https://coraka.com/")
    support_button = InlineKeyboardButton("📩 Contact Support 📩", url="https://t.me/darkkccodes")
    settings_button = InlineKeyboardButton("⚙️ Bot Settings ⚙️", callback_data="bot_settings")
    permission_button = InlineKeyboardButton("🛡 Group Permissions 🛡", callback_data="permission_settings")


    language_button = InlineKeyboardButton("🌐 Bot Language 🌐", callback_data="choose_language")
    english_button = InlineKeyboardButton("🇬🇧  English 🇬🇧 ", callback_data="choose_english")
    spanish_button = InlineKeyboardButton("🇪🇸 Spainish 🇪🇸", callback_data="choose_spanish")
    french_button = InlineKeyboardButton("🇫🇷 French 🇫🇷", callback_data="choose_french")
    italian_button = InlineKeyboardButton("🇮🇹 Italian 🇮🇹", callback_data="choose_italian")
    german_button = InlineKeyboardButton("🇩🇪 Dutch 🇩🇪", callback_data="choose_dutch")
    indian_button = InlineKeyboardButton("🇩🇪 Indian 🇩🇪", callback_data="choose_indian")


    enable_buy_alert = InlineKeyboardButton("🟤 Enable Buy Alerts", callback_data="enable_buy_alert")
    disable_buy_alert = InlineKeyboardButton("🟢 Disable Buy Alerts", callback_data="disable_buy_alert")

    enable_subscription = InlineKeyboardButton("🟤 Enable Subscription", callback_data="enable_subscription")
    disable_subscription = InlineKeyboardButton("🟢 Disable Subscription", callback_data="disable_subscription")

    if command_name=="commands":
        # --------------------------------------------------------------------
        # buttons to display when the commands has been requested
        # --------------------------------------------------------------------
        welcome_keyboard = [
            [basic_commands_button, pro_commands_button],
            [home_button]
        ]
        return welcome_keyboard

    elif command_name == "language":
        # --------------------------------------------------------------------
        # buttons to display when the language option has been initiated
        # --------------------------------------------------------------------
        welcome_keyboard = [
            [english_button, french_button],
            [german_button, indian_button],
            [italian_button, spanish_button],
            [home_button]
        ]
        return welcome_keyboard



    if group is not None and user is None and is_group:
        # --------------------------------------------------------------------
        # buttons to display inside a group
        # --------------------------------------------------------------------

        admins_button = InlineKeyboardButton(f"👫 Moderators 👫", callback_data="moderators")

        if group['website']:
            website_button = InlineKeyboardButton("🔗 Visit Website 🔗", url=group['website'])

        if group['support']:
            support_button = InlineKeyboardButton("📩 Contact Support 📩", url=group['support'])

        if group['buy_token_link'] and group['buy_token_name']:
            buy_button = InlineKeyboardButton(f"🔥 Buy {group['buy_token_name']['ticker_name'].title()} 🔥", url=group['buy_token_link'])
            welcome_keyboard = [
                [buy_button],
                [add_button],
                [trade_button],
                [commands_button],
                [support_button, website_button],
                [rules_button, admins_button],
                [settings_button, permission_button],
            ]
            return welcome_keyboard


        welcome_keyboard = [
            [add_button],
            [trade_button],
            [commands_button],
            [support_button, website_button],
            [rules_button, admins_button],
            [settings_button, permission_button],
        ]
        return welcome_keyboard

    elif group is None and user is None and not is_group:
        # --------------------------------------------------------------------
        # buttons to display when the bot first starts in a private chat
        # --------------------------------------------------------------------

        if command_name=="start":
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [language_button]
            ]
            return welcome_keyboard

    elif group is None and user is not None and not is_group:
        # --------------------------------------------------------------------
        # buttons to display when the commands has been requested
        # in a private chat with user data avaialble
        # --------------------------------------------------------------------

        if command_name=='groups_settings':
            welcome_keyboard = []

            for g in user['groups']:
                button = [InlineKeyboardButton(f"{g['name']}", url=f"http://t.me/modoraka_bot?start=groupsettings_{g['chat_id']}")]
                welcome_keyboard.append(button)

            welcome_keyboard.append([home_button])
            return welcome_keyboard

        elif command_name=='groups_permission':
            welcome_keyboard = []

            for g in user['groups']:
                button = [InlineKeyboardButton(f"{g['name']}", url=f"http://t.me/modoraka_bot?start=grouppermissions_{g['chat_id']}")]
                welcome_keyboard.append(button)

            welcome_keyboard.append([home_button])
            return welcome_keyboard

        elif command_name == "start" and not user['subscribed'] and len(user['groups']) > 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [enable_subscription],
                [enable_buy_alert],
                [settings_button, permission_button],
                [language_button]
            ]
            return welcome_keyboard

        elif command_name == "start" and user['subscribed'] and len(user['groups']) > 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [disable_subscription],
                [enable_buy_alert],
                [settings_button, permission_button],
                [language_button]
            ]
            return welcome_keyboard

        elif command_name=="start" and len(user['groups']) == 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [language_button]
            ]
            return welcome_keyboard

    elif group is not None and user is not None and not is_group:
        if command_name=='groups_settings':
            welcome_keyboard = []

            for g in user['groups']:
                button = [InlineKeyboardButton(f"{g['name']}", url=f"http://t.me/modoraka_bot?start=groupsettings_{g['chat_id']}")]
                welcome_keyboard.append(button)

            welcome_keyboard.append([home_button])
            return welcome_keyboard

        elif command_name=='groups_permission':
            welcome_keyboard = []

            for g in user['groups']:
                button = [InlineKeyboardButton(f"{g['name']}", url=f"http://t.me/modoraka_bot?start=grouppermissions_{g['chat_id']}")]
                welcome_keyboard.append(button)

            welcome_keyboard.append([home_button])
            return welcome_keyboard

        elif command_name == "start" and not user['subscribed'] and len(user['groups']) > 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [enable_subscription],
                [enable_buy_alert],
                [settings_button, permission_button],
                [language_button]
            ]
            return welcome_keyboard

        elif command_name == "start" and user['subscribed'] and len(user['groups']) > 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [disable_subscription],
                [enable_buy_alert],
                [settings_button, permission_button],
                [language_button]
            ]
            return welcome_keyboard

        elif command_name=="start" and len(user['groups']) == 0:
            welcome_keyboard = [
                [add_button],
                [trade_button],
                [support_button, website_button],
                [language_button]
            ]
            return welcome_keyboard

        elif command_name=="subscribe":
            plans_button = InlineKeyboardButton("Subscription Plans", callback_data="plans")
            subscribe_button = InlineKeyboardButton("Subcribe", callback_data="subscribe")
            welcome_keyboard = [
                [plans_button, subscribe_button],
                [home_button]
            ]
            return welcome_keyboard

    return welcome_keyboard


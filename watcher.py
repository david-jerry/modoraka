import asyncio
import django
import json
import os
import threading

from typing import List
from web3 import Web3
from asgiref.sync import sync_to_async

from utils.env_result import QUICKNODE_HTTP_URL, QUICKNODE_WS_URL, TOKEN
from utils.logger import LOGGER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.constants import ParseMode


bot = Bot(TOKEN)

with open('abi.json', 'r') as file:
    ABI = json.load(file)

with open('apps/static/buycaptionphoto.jpg', 'rb') as file:
    photo = file.read()

with open('pancake_abi.json', 'r') as file:
    PCABI = json.load(file)

with open('wrock_abi.json', 'r') as file:
    WBROCKABI = json.load(file)



buy_button = InlineKeyboardButton(
    "Buy $APE",
    url="https://rock-swap.io/#/swap?outputCurrency=0xe8a4f717ac5b08bccc7240d649af653b2577b36a",
)



w3 = Web3(Web3.WebsocketProvider(QUICKNODE_WS_URL))
LOGGER.info(f"Web3 Connected: {w3.is_connected()}")



@sync_to_async
def list_users(users):
    LOGGER.info(len(users))
    usrs = []
    for user in users:
        usrs.append(user)
    return usrs


async def handle_response(users: List[TokenAddress], message: str, token_address: str) -> None:
    usrs = await list_users(users)
    LOGGER.info(usrs)
    LOGGER.info(bot)
    for user in usrs:
        LOGGER.info(f'User: {user.chat_id} | Group: {user.group_id} | Tokens?: {user.token_address} = {token_address}')
        if user.chat_id or user.group_id and user.token_address == token_address:
            await bot.send_photo(
                chat_id=user.group_id,
                photo=photo,
                caption=message,
                parse_mode=ParseMode.HTML,
                reply_markup=welcome_markup
            )



class TokenWatcher:
    def __init__(
        self,
        w3: Web3,
        token_address: str,
        black_listed_address: str,
    ):
        self.w3 = w3
        self.token_address = token_address
        self.black_listed_address = black_listed_address

    async def watch_events(self, event, poll_interval):
        global MESSAGE
        while True:
            try:
                for e in event.get_new_entries():
                    # event = w3.eth.get_transaction(event_hash)
                    try:
                        tx = Web3.to_json(e).strip('"')
                        LOGGER.info(tx)

                        # get token information
                        tokenad = self.w3.to_checksum_address(self.token_address)
                        token_contract = self.w3.eth.contract(address=tokenad, abi=ABI)

                        token_info = TokenDetails(token_contract)
                        token_symbol = token_info.get_symbol()
                        token_liquidity: float = float(self.w3.from_wei(token_info.get_liquidity(), 'ether'))
                        token_usd: float = float(token_info.get_brock_to_usd_price())
                        token_ape_usd: float = float(token_info.get_ape_to_usd_price())
                        token_burned: float = float(self.w3.from_wei(token_info.get_burned_amount(), 'ether'))
                        token_circulating_supply: int = token_info.get_circulating_supply()

                        LOGGER.info(f"Price of APE to USD: {token_ape_usd}")

                        market_capital = float(round(self.w3.from_wei(token_circulating_supply, 'ether'), 6)) * token_ape_usd
                        liquidity_in_usd = token_liquidity * token_ape_usd

                        # Pancake Router
                        pcrouter = w3.to_checksum_address('0xeeabd314e2eE640B1aca3B27808972B05c7f6A3b') #('0x413f0E3A440abA7A15137F4278121450416882d5') # w3.to_checksum_address('0x10ED43C718714eb63d5aA57B78B54704E256024E')
                        pccont = w3.eth.contract(address=pcrouter, abi=PCABI) # (address=pcrouter, abi=WBROCKABI)

                        # get transaction details
                        transaction = self.w3.eth.get_transaction(tx)
                        to = transaction['to']
                        frm = transaction['from']
                        input_data = transaction['input']
                        amount_purchased: int = transaction['value']

                        # block position
                        block_number = transaction['blockNumber']
                        transaction_index = transaction['transactionIndex']
                        LOGGER.info(f"TXIndex: {transaction_index}")
                        latest_block_number = self.w3.eth.block_number
                        LOGGER.info(f"Latest: {latest_block_number} | TX block: {block_number}")

                        # Convert wei to ether
                        amount_in_ether: float = float(self.w3.from_wei(amount_purchased, 'ether'))
                        burned = token_burned
                        amount_in_gwei = self.w3.to_wei(amount_in_ether, 'ether')
                        LOGGER.info(round(amount_in_ether, 6))

                        # convert to usd
                        amount_in_usd: float = round(amount_in_ether, 6) * round(token_usd, 2)
                        LOGGER.info(round(amount_in_usd, 2))


                        # if the to address in the message is the router
                        if float(amount_in_usd) > float(4.9) and frm and input_data and to and to == '0xeeabd314e2eE640B1aca3B27808972B05c7f6A3b':

                            try:
                                decode = pccont.decode_function_input(input_data)
                                amount = int(amount_in_usd)
                                ape_count = calculate_logo_count(amount)
                                apes = "".join(["🦧"] * ape_count) #ape_count
                                # print the transaction and its details
                                LOGGER.info(f"decodedPath_to: {decode[1]['path'][1]}")
                                buy_address = decode[1]['path'][1]
                                buy_alert_message = f"""
<strong>APE Buy!</strong>
{apes}

💰 {round(amount_in_ether, 6)} <strong>BROCK</strong> (${round(amount_in_usd, 2)})
🪙 {amount_in_gwei} {token_symbol.upper()}
🏷️ Price: ${token_ape_usd}
🔼 Market Cap ${round(market_capital, 2)}
💧 Liquidity ${round(liquidity_in_usd, 2)}
🔎 <a href="https://scan.bit-rock.io/address/{frm}">{frm[:4]}****{frm[-4:]}</a>
⬆️ <strong>Position/TX Index</strong>: {'New' if transaction_index <= 5 else transaction_index}!

<strong>Burned</strong>: {round(burned, 6)} (${round(float(burned) * round(float(token_usd), 2), 2)} )

<a href="https://scan.bit-rock.io/tx/{tx}">TX</a> | <a href="https://thesphynx.co/swap/bitrock/0xE8a4F717Ac5b08BcCc7240D649af653b2577b36a">Chart</a> | <a href="https://apetoken.net/">Website</a> | <a href="https://twitter.com/apeonbitrock?s=21&t=jidp4vLNy_hl8VorJku59Q">Twitter</a> | <a href="https://t.me/Apeonbitrock">Telegram</a>
"""
                                LOGGER.info(buy_alert_message)
                                users = await get_all_users()
                                if buy_address == self.token_address:
                                    await handle_response(users, buy_alert_message, self.token_address)
                                else:
                                    pass
                            except Exception as e:
                                LOGGER.info(str(e))
                        else:
                            LOGGER.warning('Not what we are looking for')
                    except Exception as err:
                        LOGGER.error(f"Error: {err}")
                await asyncio.sleep(poll_interval)
            except asyncio.TimeoutError as err:
                LOGGER.error(str(err))
            except Exception as err:
                LOGGER.error(str(err))


if __name__ == "__main__":


    tx_filter = w3.eth.filter('pending')

    loop = asyncio.get_event_loop()

    try:
        while True:
            token_watcher = TokenWatcher(
                w3, token_address
            ) #  QUICKNODE_WS_URL, QUICKNODE_HTTP_URL
            loop.run_until_complete(asyncio.gather(token_watcher.watch_events(tx_filter, 2)))
            updater = Updater(TOKEN)
            updater.start_polling()
    finally:
        loop.close()



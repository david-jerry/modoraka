from django.utils.translation import gettext_lazy as _
from django.db.models import (
    BooleanField,
    CharField,
    SlugField,
    IntegerField,
    FloatField,
    ForeignKey,
    ManyToManyField,
    CASCADE,
    TextField,
)

from model_utils.models import TimeStampedModel
import requests
from utils.custom_fields import ListField
from utils.env_result import COINBASE_API, COINBASE_SK, INFURA_HTTP_URL

from coinbase.wallet.client import Client

from coinmarketcap import Market

coinmarketcap = Market()

from web3 import Web3

w3 = Web3(Web3.HTTPProvider(f"{INFURA_HTTP_URL}"))


# Create your models here.
class Tokens(TimeStampedModel):
    """
    COINMARKET CAP TICKER LIST
    ----------------------------------------------------------------------------
    This stores the total amount of tickers on the coin market cap api and extra tokens not listed on the coin market cap index
    """

    ticker_symbol = CharField(_("Token Symbol"), max_length=15, unique=True, db_index=True)
    ticker_slug = SlugField(_("Token Slug"), max_length=255)
    ticker_id = IntegerField(_("Token ID"))
    ticker_name = CharField(_("Token Name"), max_length=255)

    total_supply = FloatField(default=0.00)
    circulating_supply = FloatField(default=0.00)

    usd_price = FloatField(default=0.00)
    chf_price = FloatField(default=0.00)
    chy_price = FloatField(default=0.00)
    eur_price = FloatField(default=0.00)
    ngn_price = FloatField(default=0.00)
    gbp_price = FloatField(default=0.00)
    zar_price = FloatField(default=0.00)
    sar_price = FloatField(default=0.00)
    sek_price = FloatField(default=0.00)
    aed_price = FloatField(default=0.00)

    token_address = CharField(_("Token Contract Address"), max_length=15, blank=True)
    token_abi = TextField(_("Token Contract ABI"), blank=True)
    token_router_address = CharField(_("Token Router Address"), max_length=15, blank=True)
    token_router_abi = TextField(_("Token Router ABI"), blank=True)

    listed = BooleanField(default=False)

    def __str__(self) -> str:
        return self.ticker_name

    def contract(self):
        contract = w3.eth.contract(address=self.token_address, abi=self.token_abi)
        return contract

    def get_unknown_token_fiat_price(self, fiat: str) -> float:
        client = Client(api_key=COINBASE_API, api_secret=COINBASE_SK)
        apereq = client.get_buy_price(currency_pair=f"{self.ticker_symbol.upper()}-{fiat.upper()}")
        price = apereq["amount"]
        result = float(price)
        return round(result, 2)

    def get_unknown_token_eth_price(self, symbol: str) -> float:
        apereq = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}ETH").json()
        price = apereq["price"]
        result = float(price)
        return round(result, 2)

    @property
    def get_token_decimals(self) -> int:
        decimal = self.contract.functions.decimal().call()
        return decimal

    def get_liquidity(self) -> float:
        pair_address = self.contract.functions.pair().call()
        if pair_address:
            result = self.contract.functions.balanceOf(pair_address).call() * 2
            return result
        else:
            return 0

    def get_token_circulating_supply(self) -> int:
        if not self.listed:
            c_supply = self.contract.functions.getCirculatingSupply().call()
            return c_supply
        return self.circulating_supply

    def get_token_total_supply(self) -> int:
        if not self.listed:
            c_supply = self.contract.functions.getTotalSupply().call()
            return c_supply
        return self.total_supply

    def get_unknown_token_marketcapital(self, fiat: str) -> float:
        marketcapital = self.get_unknown_token_fiat_price(fiat) * self.get_circulating_supply()
        return round(marketcapital, 2)

    def get_token_marketcapital(self) -> float:
        marketcapital = self.usd_price * self.circulating_supply
        return round(marketcapital, 2)

    def get_token_burned_amount(self) -> float:
        burned_address = self.contract.functions.burnFeeReceiver().call()
        if burned_address:
            result = self.contract.functions.balanceOf(burned_address).call()
            return result
        else:
            return 0


class WatchToken(TimeStampedModel):
    """
    WATCH TOKEN
    ----------------------------------------------------------------------------
    This model checks if a group is in the list of groups watching a particular token
    and then alerts them if there is any exisiting watcher for the slected token
    """

    groups = ListField()
    token = ForeignKey(Tokens, on_delete=CASCADE, related_name="watched_token")

    def __str__(self):
        return f"Watched Token: {self.token.ticker_name}"


class WatchAddress(TimeStampedModel):
    """
    WATCH WALLET ADDRESS
    ----------------------------------------------------------------------------
    Stores the wallet address to watch for transaction queries to trigger a buy or sell
    action should the target address perform similar action
    """

    users = ListField()
    address = CharField(max_length=500, unique=True)
    top_earning = FloatField(default=0.00)

    def update_top_earning(self, new_price):
        pass

    def __str__(self) -> str:
        return f"Watching Address: {self.address}"

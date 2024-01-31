from __future__ import annotations

import pprint

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from coinmarketcap import Market
import requests
from utils.env_result import COINMARKETCAP_API

from utils.logger import LOGGER

# from requests_html import HTMLSession


from ...models import Tokens


class Command(BaseCommand):
    """
    Retreives all coinmarketcap tokens for their ID and Symbols
    """

    help = _("Adds or Updates all tokens from coinmarketcap")

    def handle(self, *args, **kwargs):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        params = {
            "start": 1,
            "limit": 5000,
            "sort": "symbol",
            "sort_dir": "desc",
            "convert": "USD",
        }
        headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": COINMARKETCAP_API}

        response = requests.get(url, headers=headers, params=params)
        LOGGER.info(response)
        res = response.json()

        pp = pprint.PrettyPrinter(indent=4)

        if res["status"]:
            for resp in res["data"]:
                try:
                    obj, created = Tokens.objects.get_or_create(
                        ticker_symbol=resp["symbol"],
                        defaults={
                            "ticker_symbol": resp["symbol"],
                            "ticker_slug": resp["slug"],
                            "ticker_id": resp["id"],
                            "ticker_name": resp["name"],
                            "total_supply": resp["total_supply"],
                            "circulating_supply": resp["circulating_supply"],
                            "usd_price": resp["quote"]["usd".upper()]["price"] if resp["quote"]["usd".upper()]["price"] else 0.00,
                            'listed': True
                        },
                    )
                    if created:
                        LOGGER.info(f"Successfully added {resp['name']}")
                    elif not created and obj:
                        obj.total_supply = resp['total_supply']
                        obj.circulating_supply = resp['circulating_supply']
                        obj.usd_price = resp["quote"]["usd".upper()]["price"] if resp["quote"]["usd".upper()] else obj.usd_price
                        obj.save(
                            update_fields=[
                                "total_supply",
                                "circulating_supply",
                                "usd_price",
                            ]
                        )

                except Exception as e:
                    LOGGER.error(e)
        else:
            LOGGER.error("Tokens Added Updated")

        self.stdout.write("Got all Token Details")

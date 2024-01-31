from typing import Final

import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: Final = env.bool("DJANGO_DEBUG", True)
TOKEN: Final = env('TOKEN')
DEVELOPER_ID: Final = env('DEVELOPER_ID')
USERNAME: Final = env('BOT_USERNAME')
ADMINCHATID: Final = env('ADMINCHATID')
GPTKEY: Final = env('CHATGPT_KEY')
INFURA_WS_URL: Final = env('INFURA_WS_URL')
INFURA_HTTP_URL: Final = env('INFURA_HTTP_URL')
QUICKNODE_WS_URL: Final = env('QUICKNODE_WS_URL')
QUICKNODE_HTTP_URL: Final = env('QUICKNODE_HTTP_URL')
BITROCKNODE_WS_URL: Final = env('BITROCKNODE_WS_URL')
COINBASE_PK: Final = env('COINBASE_PK')
COINBASE_KID: Final = env('COINBASE_KID')
COINBASE_API: Final = env('COINBASE_API')
COINBASE_SK: Final = env('COINBASE_SK')
COINMARKETCAP_API: Final = env('COINMARKETCAP_API')

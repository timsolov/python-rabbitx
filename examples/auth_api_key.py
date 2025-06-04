import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)
token = rabbitx.account.renew_jwt_token()["jwt"]

print(f"Token: {token}")

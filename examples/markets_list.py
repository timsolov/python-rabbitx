import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey


rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)
markets = rabbitx.markets.list()

print(f"Markets: {markets}")

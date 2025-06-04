import os
import sys
from rabbitx import RabbitX, consts
from rabbitx.apikey import read_from_json_file

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=read_from_json_file(".apikey/apiKey.json")
)
info = rabbitx.markets.info("BTC-USD")

print(f"Market info: {info}")

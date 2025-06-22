import os
import sys
import time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)
candles = rabbitx.markets.candles(
    market_id="BTC-USD",
    start_time=1,
    end_time=int(time.time()),
    period="1h",
)

print(f"Candles: {candles.result()}")

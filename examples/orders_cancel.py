import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey


rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)

# Replace with real values as needed
canceled = rabbitx.orders.cancel(market_id="BTC-USD", order_id="BTC-USD@1234").result()

print(f"Order canceled: {canceled}")

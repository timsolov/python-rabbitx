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
order = rabbitx.orders.create(
    market_id="BTC-USD", type="limit", side="long", price=10000, size=0.001
)

print(f"Order created: {order}")

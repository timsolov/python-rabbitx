import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import read_from_json_file

rabbitx = RabbitX(network=consts.ETHEREUM_MAINNET, api_key=read_from_json_file('.apikey/apiKey.json'))

# Replace with real values as needed
amended = rabbitx.orders.amend(
    order_id="BTC-USD@1234",
    market_id="BTC-USD",
    price=11000
)

print(f"Order amended: {amended}") 
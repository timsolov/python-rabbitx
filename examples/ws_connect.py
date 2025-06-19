import os
import sys
import time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey
from rabbitx.ws import WS

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)
result = rabbitx.account.renew_jwt_token().result()
token = result["jwt"]


def on_message(channel, data):
    print(f"[MESSAGE] Channel: {channel}, Data: {data}")


def on_subscribe(channel, data):
    print(f"[SUBSCRIBED] Channel: {channel}, Data: {data}")


ws = WS(
    token=token,
    network=consts.ETHEREUM_MAINNET,
    channels=["orderbook:BTC-USD"],
    on_message=on_message,
    on_subscribe=on_subscribe,
)

print("Starting WS...")
ws.start()

for i in range(10):
    time.sleep(1)
    print(f"Sleeping for {i} seconds")

print("Stopping WS...")
ws.stop()

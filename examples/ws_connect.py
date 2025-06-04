import os
import sys
import time
from rabbitx import RabbitX, consts
from rabbitx.apikey import read_from_json_file
from rabbitx.ws import WS

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=read_from_json_file(".apikey/apiKey.json")
)
token = rabbitx.account.renew_jwt_token()["jwt"]


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

ws.start()

for i in range(10):
    time.sleep(1)
    print(f"Sleeping for {i} seconds")

ws.stop()

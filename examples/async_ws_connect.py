import os
import sys
import asyncio

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import AsyncRabbitX, consts
from rabbitx.apikey import ApiKey
from rabbitx.ws import AsyncWS


async def on_message(channel, data):
    print(f"[MESSAGE] Channel: {channel}, Data: {data}")


async def on_subscribe(channel, data):
    print(f"[SUBSCRIBED] Channel: {channel}, Data: {data}")


async def main():
    async with AsyncRabbitX(
        network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
    ) as rabbitx:
        result = await rabbitx.account.renew_jwt_token()
        token = result.result()["jwt"]

        ws = AsyncWS(
            token=token,
            network=consts.ETHEREUM_MAINNET,
            channels=["orderbook:BTC-USD"],
            on_message=on_message,
            on_subscribe=on_subscribe,
        )

        await ws.create_task()
        await asyncio.sleep(10)  # Keep connection alive for 10 seconds
        await ws.cancel_task()


if __name__ == "__main__":
    asyncio.run(main())

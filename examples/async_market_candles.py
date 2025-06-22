import os
import sys
import time
import asyncio

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import AsyncRabbitX, consts
from rabbitx.apikey import ApiKey


async def main():
    async with AsyncRabbitX(
        network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
    ) as rabbitx:
        candles = await rabbitx.markets.candles(
            market_id="BTC-USD",
            start_time=1,
            end_time=int(time.time()),
            period="1h",
        )

        print(f"Candles: {candles.result()}")


if __name__ == "__main__":
    asyncio.run(main())

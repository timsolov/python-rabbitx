import os
import sys
import asyncio

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import AsyncRabbitX, consts
from rabbitx.apikey import ApiKey


async def main():
    async with AsyncRabbitX(
        network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
    ) as rabbitx:
        # Replace with real values as needed
        order = await rabbitx.orders.create(
            market_id="BTC-USD", type="limit", side="long", price=10000, size=0.001
        )
        order = order.result()

        print(f"Order created: {order}")


if __name__ == "__main__":
    asyncio.run(main())

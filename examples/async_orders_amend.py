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
        amended = await rabbitx.orders.amend(
            order_id="BTC-USD@1234", market_id="BTC-USD", price=11000
        )
        amended = amended.result()

        print(f"Order amended: {amended}")


if __name__ == "__main__":
    asyncio.run(main())

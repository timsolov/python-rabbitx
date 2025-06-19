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
        canceled = await rabbitx.orders.cancel(
            market_id="BTC-USD", order_id="BTC-USD@1234"
        )
        canceled = canceled.result()

        print(f"Order canceled: {canceled}")


if __name__ == "__main__":
    asyncio.run(main())

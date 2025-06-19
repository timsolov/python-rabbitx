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
        result = await rabbitx.orders.cancel_all()
        result = result.result()

        print(f"Cancel all result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

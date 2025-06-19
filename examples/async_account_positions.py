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
        positions = await rabbitx.account.positions()
        positions = positions.result()

        print(f"Positions: {positions}")


if __name__ == "__main__":
    asyncio.run(main())

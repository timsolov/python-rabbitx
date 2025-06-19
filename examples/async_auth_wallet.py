import os
import sys
import asyncio

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import AsyncRabbitX, consts
from rabbitx.wallet import Wallet


async def main():
    async with AsyncRabbitX(
        network=consts.ETHEREUM_MAINNET,
        wallet=Wallet.from_file(".wallets/wallet.pk"),
    ) as rabbitx:
        result = await rabbitx.account.onboarding()
        token = result.result()["jwt"]

        print(f"Token: {token}")


if __name__ == "__main__":
    asyncio.run(main())

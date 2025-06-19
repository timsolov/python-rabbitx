import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from rabbitx import RabbitX, consts
from rabbitx.wallet import Wallet


rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, 
    wallet=Wallet.from_file(".wallets/wallet.pk"),
)
result = rabbitx.account.onboarding().result()
token = result["jwt"]

print(f"Token: {token}")

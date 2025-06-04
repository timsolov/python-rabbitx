import os
import sys
from rabbitx import RabbitX, consts
from rabbitx.xutils import read_file

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, wallet=read_file(".wallets/wallet.pk")
)
token = rabbitx.account.onboarding()["jwt"]

print(f"Token: {token}")

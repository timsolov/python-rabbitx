# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "web3",
# ]
# ///
from web3 import Web3
import os

w3 = Web3()

root_dir = os.path.dirname(os.path.dirname(__file__))


def generate_wallet_file(directory: str):
    i = 1
    while True:
        filename = f"wallet{i}.pk"
        wallet_file = os.path.join(directory, filename)
        if not os.path.exists(wallet_file):
            break
        i += 1

    return wallet_file


def generate_wallet():
    account = w3.eth.account.create()

    private_key = w3.to_hex(account.key)

    wallet_file = generate_wallet_file(os.path.join(root_dir, ".wallets"))

    # Save private key to file
    with open(wallet_file, "w") as f:
        f.write(private_key)

    # Print wallet information
    print("\nWallet generated successfully!")
    print(f"Private key: {private_key}")
    print(f"Ethereum address: {account.address}")
    print(f"\nWallet information saved to: {wallet_file}")


if __name__ == "__main__":
    generate_wallet()

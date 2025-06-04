# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "eth-account",
# ]
# ///
from eth_account import Account
import os


def read_wallet(wallet_file):
    # Check if wallet file exists
    if not os.path.exists(wallet_file):
        print(f"No wallet found for address: {wallet_file}")
        return None

    # Read the private key from file
    with open(wallet_file, "r") as f:
        private_key = f.read().strip()

    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    # Create an Ethereum account from the private key
    account = Account.from_key(private_key)

    # Print wallet information
    print("\nWallet information:")
    print(f"Private key: {private_key}")
    print(f"Ethereum address: {account.address}")

    return account


if __name__ == "__main__":
    path = input("Enter path to wallet file: ")
    read_wallet(path)

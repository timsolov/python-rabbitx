from eth_account import Account
import secrets
import os
from datetime import datetime
from web3 import Web3

w3 = Web3()

def generate_wallet():
    account = w3.eth.account.create()

    private_key = w3.to_hex(account.key)
    
    # Create wallet info directory if it doesn't exist
    wallet_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.wallet')
    
    # Save private key to file
    with open(wallet_file, 'w') as f:
        f.write(private_key)
    
    # Print wallet information
    print("\nWallet generated successfully!")
    print(f"Private key: {private_key}")
    print(f"Ethereum address: {account.address}")
    print(f"\nWallet information saved to: {wallet_file}")

if __name__ == "__main__":
    generate_wallet() 
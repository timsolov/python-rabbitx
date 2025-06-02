from eth_account import Account

if __name__ == "__main__":
    mnemonic = input("Enter your recovery phrase (words separated by spaces): ").strip()
    try:
        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(mnemonic)
        private_key = account.key.hex()
        print("\nRecovered private key:", private_key)
        print("Ethereum address:", account.address)
    except Exception as e:
        print("Error recovering private key from phrase:", e)

from eth_account import Account
from .xutils import read_file

Account.enable_unaudited_hdwallet_features()

class Wallet:
    def __init__(self, private_key:str):
        self.private_key = private_key

    @staticmethod
    def from_file(private_key_path:str) -> 'Wallet':
        """
        Read the private key from a file.

        :param path: The path to the file
        :type path: str
        :return: The private key
        :rtype: Wallet
        
        Example:

        .. code-block:: python

            from rabbitx.wallet import Wallet
            wallet = Wallet.from_file(".wallets/wallet.pk")
            print(wallet)
        """
        return Wallet(read_file(private_key_path).strip())

    @staticmethod
    def from_mnemonic(mnemonic:str) -> 'Wallet':
        """
        Get the private key from a mnemonic phrase.

        :param mnemonic: The mnemonic
        :type mnemonic: str
        :return: The private key
        :rtype: Wallet

        Example:

        .. code-block:: python

            from rabbitx.wallet import Wallet
            wallet = Wallet.from_mnemonic("your mnemonic phrase")
            print(wallet)
        """
        return Account.from_mnemonic(mnemonic).key.hex()
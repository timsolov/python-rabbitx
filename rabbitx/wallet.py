from eth_account import Account
from .xutils import read_file

Account.enable_unaudited_hdwallet_features()


class Wallet:
    """
    A wallet object.

    Attributes
    ----------
    private_key : str
        The private key
    """

    def __init__(self, private_key: str):
        self.private_key = private_key

    @staticmethod
    def from_file(private_key_path: str) -> "Wallet":
        """
        Read the private key from a file.

        :param private_key_path: The path to the file
        :type private_key_path: str
        :return: The wallet object
        :rtype: Wallet

        Example:

        .. code-block:: python

            from rabbitx.wallet import Wallet
            wallet = Wallet.from_file(".wallets/wallet.pk")
            print(wallet)
        """
        return Wallet(read_file(private_key_path).strip())

    @staticmethod
    def from_mnemonic(mnemonic: str) -> "Wallet":
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
        return Wallet(Account.from_mnemonic(mnemonic).key.hex())

    def address(self) -> str:
        """
        Get the wallet address

        :return: The wallet address
        :rtype: str
        """
        return Account.from_key(self.private_key).address
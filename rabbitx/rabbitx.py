from .consts import API_URL, CHAIN_ID, EIP712_DOMAIN, EIP712_MESSAGE, EID
from .apikey import ApiKey
from .wallet import Wallet
from .signer import ApiSigner, EIP712Signer
from .client import Client
from .orders import Orders
from .markets import Markets
from .account import Account
from .vaults import Vaults


class RabbitX:
    """
    RabbitX class.

    This class is a wrapper around the RabbitX API.

    Attributes
    ----------
    client : Client
        The client object
    account : Account
        The account object
    orders : Orders
        The orders object
    vaults : Vaults
        The vaults object
    markets : Markets
        The markets object
    """

    def __init__(
        self,
        network: str,
        wallet: Wallet = None,
        api_key: ApiKey = None,
        base_url: str = None,
    ):
        """
        :param network: The network to use (supported: "ethereum", "ethereum-sepolia", "blast", "blast-sepolia")
        :type network: str
        :param wallet: The wallet to use.
        :type wallet: Wallet
        :param api_key: The API key to use.
        :type api_key: ApiKey
        :param base_url: The base URL to override the default base URL for the network.
        :type base_url: str
        """

        if wallet is not None and api_key is not None:
            raise Exception("Cannot provide both wallet and api_key")
        if wallet is None and api_key is None:
            raise Exception("Must provide either wallet or api_key")
        if network not in API_URL:
            raise ValueError(f"Invalid network: {network}")

        self.network = network

        if wallet:
            self.signer = EIP712Signer(
                private_key=wallet.private_key,
                chain_id=CHAIN_ID[network],
                domain=EIP712_DOMAIN[network],
                message=EIP712_MESSAGE[network],
            )
        else:
            self.signer = ApiSigner(api_key=api_key)

        if not base_url:
            base_url = API_URL[network]

        self.client = Client(
            base_url=base_url, signer=self.signer, headers={"EID": EID[network]}
        )

        self.account = Account(self.client)
        self.orders = Orders(self.client)
        self.markets = Markets(self.client)
        self.vaults = Vaults(self.client)

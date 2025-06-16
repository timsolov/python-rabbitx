from .consts import API_URL, CHAIN_ID, EIP712_DOMAIN, EIP712_MESSAGE, EID
from .apikey import ApiKey
from .wallet import Wallet
from .signer import ApiSigner, EIP712Signer
from .transport import SyncTransport, AsyncTransport
from .orders import Orders, AsyncOrders
from .markets import Markets, AsyncMarkets
from .account import Account, AsyncAccount
from .vaults import Vaults, AsyncVaults


class RabbitX:
    """
    RabbitX class.

    This class is a wrapper around the RabbitX API.

    Attributes
    ----------
    transport : Transport
        The transport object
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
        wallet: Wallet | None = None,
        api_key: ApiKey | None = None,
        base_url: str | None = None,
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

        self._validate_auth(wallet, api_key)
        self._validate_network(network)

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

        self.transport = SyncTransport(
            base_url=base_url, signer=self.signer, headers={"EID": EID[network]}
        )

        self.account = Account(self.transport)
        self.orders = Orders(self.transport)
        self.markets = Markets(self.transport)
        self.vaults = Vaults(self.transport)

    def _validate_auth(self, wallet: Wallet, api_key: ApiKey):
        """
        Raises an Exception if both wallet and api_key are provided.
        Raises an Exception if neither wallet nor api_key are provided.
        """
        auth_provided = 0
        if wallet:
            auth_provided += 1
        if api_key:
            auth_provided += 1

        if auth_provided > 1:
            raise Exception("Cannot provide both wallet and api_key")
        if auth_provided == 0:
            raise Exception("Must provide either wallet or api_key")

    def _validate_network(self, network: str):
        """
        Raises an Exception if the network is invalid.
        """
        if network not in API_URL:
            raise ValueError(f"Unknown network: {network}")


class AsyncRabbitX(RabbitX):
    __doc__ = RabbitX.__doc__

    def __init__(self, network: str, wallet: Wallet | None = None, api_key: ApiKey | None = None, base_url: str | None = None):
        super().__init__(network, wallet, api_key, base_url)

        self.transport = AsyncTransport(
            base_url=base_url, signer=self.signer, headers={"EID": EID[network]}
        )

        self.account = AsyncAccount(self.transport)
        self.orders = AsyncOrders(self.transport)
        self.markets = AsyncMarkets(self.transport)
        self.vaults = AsyncVaults(self.transport)
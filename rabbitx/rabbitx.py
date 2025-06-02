from .consts import *
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

    def __init__(self, network:str, wallet_pk:str=None, api_key:str=None, base_url:str=None):
        """
        :param network: The network to use (supported: "ethereum", "ethereum-sepolia", "blast", "blast-sepolia")
        :type network: str
        :param wallet_pk: The private key of the wallet to use.
        :type wallet_pk: str
        :param api_key: The API key to use.
        :type api_key: str
        :param base_url: The base URL to override the default base URL for the network.
        :type base_url: str
        """

        if wallet_pk and api_key:
            raise Exception("Cannot provide both wallet_pk and api_key")
        if not wallet_pk and not api_key:
            raise Exception("Must provide either wallet_pk or api_key")
        if network and not network in API_URL:
            raise ValueError(f'Invalid network: {network}')
        
        self.network = network
            
        if wallet_pk:
            self.signer = EIP712Signer(private_key=wallet_pk, chain_id=CHAIN_ID[network], domain=EIP712_DOMAIN[network], message=EIP712_MESSAGE[network])
        else:
            self.signer = ApiSigner(api_key=api_key)

        if not base_url:
            base_url = API_URL[network]
        
        self.client = Client(base_url=base_url, signer=self.signer, headers={'EID': EID[network]})
        
        self.account = Account(self.client)
        self.orders = Orders(self.client)
        self.markets = Markets(self.client)
        self.vaults = Vaults(self.client)



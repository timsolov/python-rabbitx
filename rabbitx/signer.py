from abc import ABC, abstractmethod
from rabbitx.xutils import new_payload, payload_hash, rbt_signature
from rabbitx.xtime import get_current_timestamp
from rabbitx.apikey import ApiKey

class Signer(ABC):
    """
    Signer class.

    This class is a base implementation of the Signer interface.
    """
    @abstractmethod
    def headers(self, method:str, endpoint:str, payload={}) -> dict:
        pass
    
class ApiSigner(Signer):
    """
    ApiSigner class.

    This class is used to sign requests using the API key.

    Attributes
    ----------
    api_key : ApiKey
        The API key to use for signing
    """
    def __init__(self, api_key:ApiKey):
        self.api_key = api_key

    def headers(self, method:str, endpoint:str, payload={}) -> dict:
        timestamp = get_current_timestamp()+15
        sorted_payload = new_payload(method.upper(), endpoint, params=payload)
        hashed_payload = payload_hash(timestamp, sorted_payload)
        signature = rbt_signature(hashed_payload, self.api_key.secret)
        
        headers = {
            "RBT-TS": str(timestamp),
            'RBT-API-KEY': self.api_key.key,
            "RBT-SIGNATURE": signature,
        }

        return headers

from rabbitx.eip712 import eip712_message, sign_message
from binascii import hexlify, unhexlify
from eth_account import Account

class EIP712Signer(Signer):
    """
    EIP712Signer class.

    This class is used to sign requests using the EIP-712 message.

    Attributes
    ----------
    private_key : str
        The private key to use for signing
    chain_id : int
        The chain ID to use for signing
    domain : str
        The domain to use for signing
    message : str
        The message to sign
    """
    def __init__(self, private_key:str, chain_id:int, domain:str, message:str):
        self.private_key = private_key
        self.chain_id = chain_id
        self.domain = domain
        self.message = message
        account = Account.from_key(private_key)
        self.wallet = account.address

    def headers(self, method:str, endpoint:str, payload={}) -> dict:
        timestamp = get_current_timestamp() + 15 # shift timestamp 15 seconds into the future
        eip712_payload = eip712_message(self.chain_id, timestamp, self.domain, self.message)
        signature = sign_message(message=eip712_payload, private_key=self.private_key)
        
        headers = {
            "RBT-PK-TS": str(timestamp),
            "RBT-TS": str(timestamp),
            "RBT-PK-SIGNATURE": signature,
        }

        return headers

class JWTTokenSigner(Signer):
    """
    JWTTokenSigner class.

    This class is used to sign requests using the JWT token.

    Attributes
    ----------
    jwt_token : str
        The JWT token to use for signing
    refresh_token : str
        The refresh token to use for signing
    random_secret : str
        The random secret to use for signing
    """
    def __init__(self, jwt_token:str, refresh_token:str, random_secret:str):
        self.jwt_token = jwt_token
        self.refresh_token = refresh_token
        self.random_secret = random_secret

    def headers(self, method:str, endpoint:str, payload={}) -> dict:
        timestamp = get_current_timestamp()+15
        sorted_payload = new_payload(method.upper(), endpoint, params=payload)
        hashed_payload = payload_hash(timestamp, sorted_payload)
        signature = rbt_signature(hashed_payload, self.random_secret)

        headers = {
            "RBT-SIGNATURE": signature,
            "RBT-TS": str(timestamp),
            "RBT-JWT": self.jwt_token,
        }

        return headers
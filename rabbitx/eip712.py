from eth_account import Account
from eth_account.messages import SignableMessage
from eth_account.messages import encode_typed_data, SignableMessage

def eip712_message(chainID:int, timestamp:int, domain:str, message:str) -> SignableMessage:
    """
    Create an EIP-712 message.

    :param chainID: The chain ID
    :type chainID: int
    :param timestamp: The timestamp
    :type timestamp: int
    :param domain: The domain
    :type domain: str
    :param message: The message
    :type message: str
    :return: The EIP-712 message
    :rtype: SignableMessage
    """
    
    EIP712_TYPES = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            # {"name": "verifyingContract", "type": "address"},
        ],
        "signin": [
            {"name": "message", "type": "string"},
            {"name": "timestamp", "type": "uint256"},
        ]
    }
    
    EIP712_DOMAIN = {
        "name": domain_name,
        "version": "1",
        "chainId": chainID,
        # "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC"
    }
    
    structured_data = {
        "types": EIP712_TYPES,
        "domain": EIP712_DOMAIN,
        "primaryType": "signin",
        "message": {
            "message": message,
            "timestamp": timestamp,
        },
    }

    # Encode the structured data using eth_account
    try:
        eip712_msg = encode_typed_data(full_message=structured_data)
    except ValueError as e:
        print(f"Failed to encode EIP712 message: {e}")
        return None

    return eip712_msg

def sign_message(message, private_key) -> str:
    """
    Sign a message using the EIP-712 message.

    :param message: The message to sign
    :type message: SignableMessage
    :param private_key: The private key to use for signing
    :type private_key: str
    :return: The signed message
    :rtype: str
    """
    signed_message = Account.sign_message(message, private_key=private_key)
    signature = signed_message.signature.hex()
    if signature.startswith("0x"):
        return signature
    else:
        return "0x" + signature

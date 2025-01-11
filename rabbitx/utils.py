import hashlib
from binascii import hexlify, unhexlify
from utils.time import get_current_timestamp

def new_payload(method: str, endpoint: str, params: dict) -> list:
    """
    Creates a payload dictionary with sorted keys.

    Args:
        timestamp: Unix timestamp (int).
        method: HTTP method (str, e.g., "POST").
        endpoint: API endpoint path (str, e.g., "/orders").
        params: Dictionary of request parameters.

    Returns:
        List of dictionaries representing the payload with sorted keys.
    """

    payload = [
        {"key": key, "value": value} for key, value in sorted(params.items())
    ]
    payload.extend([{"key": "method", "value": method}, {"key": "path", "value": endpoint}])
    return payload

def payload_hash(timestamp: int, payload: list) -> str:
    """
    Hashes the payload with SHA-256 after sorting keys and formatting the message.

    Args:
        timestamp: Unix timestamp (int).
        payload: List of dictionaries representing the payload.

    Returns:
        SHA-256 hash of the formatted payload string (str).
    """
    
    # Sort payload by key
    sorted_payload = sorted(payload, key=lambda x: x["key"])

    message_parts = []
    for item in sorted_payload:
        key, value = item["key"], item["value"]
        if isinstance(value, list):
            # Join array values with commas and wrap in double quotes
            message_parts.append(f'{key}=["{",".join(map(str, value))}"]')
        else:
            message_parts.append(f"{key}={value}")

    message = "".join(message_parts) + str(timestamp)
    encoded_message = message.encode("utf-8")
    return  "0x" + hashlib.sha256(encoded_message).hexdigest()

def rbt_signature(payload: str, random_secret: str) -> str:
    """
    Computes the RBT signature (SHA-256 HMAC) using the provided secret.

    Args:
        payload: Hashed payload string (str).
        random_secret: API secret key (str).

    Returns:
        Base64-encoded HMAC string (str).
    """

    import hmac 
    
    # Convert key and data to bytes if provided as hexadecimal strings
    key_bytes = unhexlify(random_secret[2:] if random_secret.startswith("0x") else random_secret)
    data_bytes = unhexlify(payload[2:] if payload.startswith("0x") else payload)

    # Compute HMAC and convert result to hexadecimal
    hmac_obj = hmac.new(key_bytes, data_bytes, hashlib.sha256)
    return "0x" + hexlify(hmac_obj.digest()).decode()


def create_headers(timestamp: int, rbt_signature: str, jwt:str) -> dict:
    """
    Creates headers dictionary with RBT-related headers and optional request headers.

    Args:
        timestamp: Unix timestamp (int).
        payload_hash: SHA-256 hash of the payload (str).
        rbt_signature: RBT signature string (str).
        request_headers: Optional dictionary of additional request headers (default: None).

    Returns:
        Dictionary containing RBT-SIGNATURE, RBT-TS, and potentially other headers.
    """

    headers = {
        "RBT-SIGNATURE": rbt_signature,
        "RBT-TS": str(timestamp),
        "RBT-JWT": jwt,   
    }

    return headers


def api_headers(method:str, endpoint:str, api_key:str, api_secret:str, json={}) -> dict:
    timestamp = get_current_timestamp()+15
    payload = new_payload(method.upper(), endpoint, params=json)
    hashed_payload = payload_hash(timestamp, payload)
    signature = rbt_signature(hashed_payload, api_secret)
    
    headers = {
        "RBT-TS": str(timestamp),
        'RBT-API-KEY': api_key,
        "RBT-SIGNATURE": signature,
    }

    return headers
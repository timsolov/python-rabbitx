import hashlib
from binascii import hexlify, unhexlify
import json
from pygments import highlight, lexers, formatters

from rabbitx.xtime import get_current_timestamp

def new_payload(method: str, endpoint: str, params: dict) -> list:
    """
    Creates a payload dictionary with sorted keys.

    :param method: HTTP method (str, e.g., "POST")
    :type method: str
    :param endpoint: API endpoint path (str, e.g., "/orders")
    :type endpoint: str
    :param params: Dictionary of request parameters
    :type params: dict
    :return: List of dictionaries representing the payload with sorted keys
    :rtype: list
    """

    payload = [
        {"key": key, "value": str(value).lower() if isinstance(value, bool) else value} for key, value in sorted(params.items())
    ]
    payload.extend([{"key": "method", "value": method}, {"key": "path", "value": endpoint}])
    return payload

def payload_hash(timestamp: int, payload: list) -> str:
    """
    Hashes the payload with SHA-256 after sorting keys and formatting the message.

    :param timestamp: Unix timestamp (int)
    :type timestamp: int
    :param payload: List of dictionaries representing the payload
    :type payload: list
    :return: SHA-256 hash of the formatted payload string
    :rtype: str
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

    :param payload: Hashed payload string
    :type payload: str
    :param random_secret: API secret key
    :type random_secret: str
    :return: Base64-encoded HMAC string
    :rtype: str
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

    :param timestamp: Unix timestamp
    :type timestamp: int
    :param rbt_signature: RBT signature string
    :type rbt_signature: str
    :param jwt: JWT token
    :type jwt: str
    :return: Dictionary containing RBT-SIGNATURE, RBT-TS, and potentially other headers
    :rtype: dict
    """

    headers = {
        "RBT-SIGNATURE": rbt_signature,
        "RBT-TS": str(timestamp),
        "RBT-JWT": jwt,   
    }

    return headers


def api_headers(method:str, endpoint:str, api_key:str, api_secret:str, json={}) -> dict:
    """
    Creates headers for API requests.

    :param method: HTTP method (str, e.g., "POST")
    :type method: str
    :param endpoint: API endpoint path (str, e.g., "/orders")
    :type endpoint: str
    :param api_key: API key
    :type api_key: str
    :param api_secret: API secret
    :type api_secret: str
    :param json: JSON payload
    :type json: dict
    :return: Dictionary containing RBT-SIGNATURE, RBT-TS, and potentially other headers
    :rtype: dict
    """
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

def read_file(file_path:str) -> str:
    """
    Reads a file and returns its contents.

    :param file_path: Path to the file
    :type file_path: str
    :return: The contents of the file
    :rtype: str
    """
    with open(file_path, 'r') as file:
        return file.read()

def print_json(result, color=True):
    """
    Prints a JSON object with optional color formatting.

    :param result: JSON object to print
    :type result: dict
    :param color: Whether to use color formatting
    :type color: bool
    """
    formatted_json = json.dumps(result, indent=4)
    if color:
        formatted_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(formatted_json)

def dict_has_path(d: dict, path: str) -> bool:
    """
    Checks if a dictionary has a specific path.

    :param d: Dictionary to check
    :type d: dict
    :param path: Path to check in the dictionary
    :type path: str
    :return: True if the path exists, False otherwise
    :rtype: bool
    """
    keys = path.split('.')
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    return True

def dict_get_path(d: dict, path: str) -> any:
    """
    Gets a value from a dictionary by path.

    :param d: Dictionary to get the value from
    :type d: dict
    :param path: Path to the value in the dictionary
    :type path: str
    :return: The value at the path, or None if the path does not exist
    :rtype: any
    """
    keys = path.split('.')
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current
from eth_account.messages import encode_typed_data

# Function to encode EIP-712 message
def create_message(domain_name, message, timestamp):
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
        "chainId": 1,
        # "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC"
    }
    
    structured_data = {
        "types": EIP712_TYPES,
        "domain": EIP712_DOMAIN,
        "primaryType": "signin",
        "message": {
            "message": message,
            "timestamp": int(timestamp),
        },
    }

    # Encode the structured data using eth_account
    try:
        eip712_msg = encode_typed_data(full_message=structured_data)
    except ValueError as e:
        print(f"Failed to encode EIP712 message: {e}")
        return None

    return eip712_msg

# Example usage
# message = "Hello, this is a test message"
# timestamp = 1234567890  # Example timestamp
# encoded_msg = eip712_message(message, timestamp)

# if encoded_msg:
#     print("Encoded EIP712 Message:", encoded_msg)
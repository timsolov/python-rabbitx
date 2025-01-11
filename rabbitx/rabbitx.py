import requests

EIP712_DOMAIN = "RabbitXId"
EIP712_MESSAGE = "Welcome to RabbitX!\n\nClick to sign in and on-board your wallet for trading perpetuals.\n\nThis request will not trigger a blockchain transaction or cost any gas fees. This signature only proves you are the true owner of this wallet.\n\nBy signing this message you agree to the terms and conditions of the exchange."

BASE_URL = "https://api.prod.rabbitx.io"

# Onboarding request with wallet and signature
def onboarding(wallet, signature, timestamp):
    payload = {
        "is_client": True,
        "wallet": wallet,
        "signature": signature,
    }
    headers = {
        "Content-Type": "application/json",
        "RBT-PK-TS": str(timestamp),
        "RBT-TS": str(timestamp),
    }
    response = requests.post(
        url=BASE_URL + "/onboarding",
        headers=headers, 
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    
    print(response.text)
    
    return None

def account_validate(jwt):
    headers = {
        "RBT-JWT": jwt,
    }
    
    response = requests.get(
        url=BASE_URL + "/account/validate",
        headers=headers
    )
    
    if response.status_code == 200:
        return True
    
    print(response.text)
    
    return False
